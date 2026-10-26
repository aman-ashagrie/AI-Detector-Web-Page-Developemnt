import logging
import re
import unicodedata
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("is-it-ai")

models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        models["vectorizer"] = joblib.load(Path(__file__).parent / "models" / "vectorizer.joblib")
        models["log_reg"] = joblib.load(Path(__file__).parent / "models" / "logreg.joblib")
        models["naive_bayes"] = joblib.load(Path(__file__).parent / "models" / "naive_bayes.joblib")
        logger.info("Models loaded successfully.")
    except FileNotFoundError as e:
        logger.error(f"Could not find model files: {e}")
    yield
    models.clear()

#Add in dataset cleaning functions from Assignment 2

def clean_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\u00a0\u00c2\u200b-\u200f\u202f\u3000\ufeff]", " ", text)
    text = re.sub(r"https?://\S+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"www\.\S+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b", " ", text)
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    text = re.sub(r"â€™|â€œ|â€\x9d|â€|Â|\ufffd", " ", text)
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


app = FastAPI(title="Is It AI?", lifespan=lifespan)

class AnalyzeRequest(BaseModel):
    text: str

#Health Check
@app.get("/api/health")
def health_check():
    return {
        "status": "ok", 
        "models_loaded": len(models) == 3
    }

#Analysis
@app.post("/api/analyze")
def analyze_text(request: AnalyzeRequest):

    sentences = split_sentences(request.text)
    if not sentences:
        raise HTTPException(status_code=400, detail="No readable sentences found.")
    X = models["vectorizer"].transform(sentences)
    p_lr = models["log_reg"].predict_proba(X)[:, 1]
    p_nb = models["naive_bayes"].predict_proba(X)[:, 1]
    p_avg = (p_lr + p_nb) / 2
    final_score = float(p_avg.mean()) * 100

    return {"score": round(final_score, 2)}




