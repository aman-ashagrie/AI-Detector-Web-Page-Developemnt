import logging
import os
import re
import threading
import unicodedata
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("is-it-ai")

# DoS defence settings (set DOS_DEFENCES=off to demonstrate the attack)
DOS_DEFENCES = os.getenv("DOS_DEFENCES", "on") == "on"
MAX_CHARS = 10_000
MAX_BODY_BYTES = 128_000
MAX_CONCURRENT = 4
analysis_slots = threading.BoundedSemaphore(MAX_CONCURRENT)

FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

print(f"DoS defences: {'ON' if DOS_DEFENCES else 'OFF'} (max {MAX_CONCURRENT} concurrent analyses)")

MODEL_DIR = Path(__file__).parent / "models"
models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        models["vectorizer"] = joblib.load(MODEL_DIR / "vectorizer.joblib")
        models["log_reg"] = joblib.load(MODEL_DIR / "logreg.joblib")
        models["naive_bayes"] = joblib.load(MODEL_DIR / "naive_bayes.joblib")
        logger.info("Models loaded successfully.")
    except FileNotFoundError as e:
        logger.error(f"Could not find model files: {e}")
        raise RuntimeError("Model files missing, server not started.") from e
    yield
    models.clear()


# Text cleaning, same as Assignment 2 training

def strip_blocks(text, tag):
    # Linear-time replacement for the <script>/<style> regex
    lower = text.lower()
    out = []
    i = 0
    while True:
        start = lower.find("<" + tag, i)
        if start == -1:
            break
        end = lower.find("</" + tag + ">", start)
        if end == -1:
            break
        out.append(text[i:start])
        out.append(" ")
        i = end + len(tag) + 3
    out.append(text[i:])
    return "".join(out)


def clean_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[ Â​-‏ 　﻿]", " ", text)
    text = re.sub(r"https?://\S+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"www\.\S+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b[\w.+-]{1,64}@[\w-]{1,253}(?:\.[\w-]{1,63})+\b", " ", text)
    if DOS_DEFENCES:
        text = strip_blocks(text, "script")
        text = strip_blocks(text, "style")
    else:
        text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    text = re.sub(r"â€™|â€œ|â€\x9d|â€|Â|�", " ", text)
    text = re.sub(r"[^\S\n]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)
    return text.strip()


def split_sentences(text):
    text = clean_text(text)
    sentences = []
    for para in re.split(r"\n+", text):
        para = para.strip()
        if not para:
            continue
        for sent in re.split(r"(?<=[.!?])\s*(?=[A-Z])", para):
            sent = sent.strip()
            if sent:
                sentences.append(sent)
    return sentences


app = FastAPI(
    title="Is It AI?",
    description="Detects whether a piece of text is likely to be AI-generated.",
    lifespan=lifespan,
)


# Consistent JSON error format

def error_response(status_code, message):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": status_code, "message": message}},
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return error_response(exc.status_code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    loc = first.get("loc") or ()
    field = loc[-1] if loc and isinstance(loc[-1], str) else "body"
    return error_response(422, f"{field}: {first['msg']}")


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    logger.exception("Unexpected error")
    return error_response(500, "Internal server error.")


# Middleware (the last one added runs first, so security headers wrap CORS and errors)

@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    if DOS_DEFENCES and request.method == "POST":
        length = request.headers.get("content-length")
        if length is None:
            return error_response(411, "Content-Length header required.")
        if not length.isdigit() or int(length) > MAX_BODY_BYTES:
            return error_response(413, "Request body too large.")
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unexpected error")
        response = error_response(500, "Internal server error.")
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


# Request and response models

class AnalyzeRequest(BaseModel):
    text: str = Field(
        min_length=20,
        max_length=MAX_CHARS if DOS_DEFENCES else None,
        description="The text to check, 20 to 10,000 characters.",
        examples=["The industrial revolution changed how people worked. Factories replaced small workshops."],
    )


class SentenceScore(BaseModel):
    text: str
    score: float = Field(description="AI likelihood for this sentence, 0 to 100.")


class AnalyzeResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "score": 72.4,
                    "sentences": [
                        {"text": "Intelligent systems are becoming more fluent.", "score": 81.0},
                        {"text": "I walked to the shops after lunch.", "score": 63.8},
                    ],
                }
            ]
        }
    )

    score: float = Field(description="Overall AI likelihood, 0 to 100.")
    sentences: list[SentenceScore]


class HealthResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"status": "ok", "models_loaded": True}]}
    )

    status: str
    models_loaded: bool


class ErrorBody(BaseModel):
    code: int = Field(description="The HTTP status code.")
    message: str = Field(description="A short, safe description of what went wrong.")


class ErrorResponse(BaseModel):
    error: ErrorBody


def error_doc(code, description, message):
    return {
        "model": ErrorResponse,
        "description": description,
        "content": {"application/json": {"example": {"error": {"code": code, "message": message}}}},
    }


# Endpoints

@app.get("/api/health", response_model=HealthResponse, summary="Check the server and models are ready")
def health_check():
    return {"status": "ok", "models_loaded": len(models) == 3}


@app.post(
    "/api/analyse/",
    response_model=AnalyzeResponse,
    summary="Score text for AI likelihood",
    responses={
        400: error_doc(400, "No readable sentences in the text", "No readable sentences found."),
        411: error_doc(411, "Missing Content-Length header", "Content-Length header required."),
        413: error_doc(413, "Request body larger than 128,000 bytes", "Request body too large."),
        422: error_doc(
            422,
            "Text missing, shorter than 20 or longer than 10,000 characters",
            "text: String should have at least 20 characters",
        ),
        503: error_doc(503, "All analysis slots are busy; try again shortly", "Server busy, please try again shortly."),
    },
)

def analyze_text(request: AnalyzeRequest):
    if DOS_DEFENCES and not analysis_slots.acquire(blocking=False):
        raise HTTPException(status_code=503, detail="Server busy, please try again shortly.")
    try:
        sentences = split_sentences(request.text)
        if not sentences:
            raise HTTPException(status_code=400, detail="No readable sentences found.")
        X = models["vectorizer"].transform(sentences)
        p_lr = models["log_reg"].predict_proba(X)[:, 1]
        p_nb = models["naive_bayes"].predict_proba(X)[:, 1]
        p_avg = (p_lr + p_nb) / 2

        return {
            "score": round(float(p_avg.mean()) * 100, 2),
            "sentences": [
                {"text": sentence, "score": round(float(p_avg[i]) * 100, 2)}
                for i, sentence in enumerate(sentences)
            ],
        }
    finally:
        if DOS_DEFENCES:
            analysis_slots.release()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, server_header=False)
