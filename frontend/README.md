# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## Setup and running

**Requirements:** Python 3.11+ (tested on 3.14), Node.js 18+ and npm.

### Back end
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --no-server-header
```
The console prints `DoS defences: ON` and the server runs at http://127.0.0.1:8000. Interactive API documentation is at **http://127.0.0.1:8000/docs**.

> Windows note: if `pip` fails with a "long path" error, move the project to a short path (e.g. the Desktop) or enable Windows long-path support.

### Front end
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173**. The back end only accepts requests from this origin (CORS).


## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## API

| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|
| GET | `/api/health` | Check the server is up and the models are loaded | 200 `{"status","models_loaded"}` | – |
| POST | `/api/analyse/` | Score text for AI likelihood | 200 `{"score","sentences":[{"text","score"}]}` | 400, 411, 413, 422, 503 |

Request: `{"text": "20 to 10,000 characters"}`. Every endpoint is described with an example in `/docs`.
Every error response has the same shape: `{"error": {"code": 422, "message": "text: String should have at least 20 characters"}}`.

---

## Threat model

**Who would attack it?**
1. A student, or a "humaniser" service, that wants AI-generated text to be judged human-written.
2. Someone who wants to take the service down, so it can't be used to check their work, or just to cause disruption.

**What are they trying to achieve?**
To make the detector unavailable or slow for real users, to find out how it makes decisions by probing it repeatedly, or to learn about our server from its error messages and headers.

**What can they actually do?**
Attackers don't use our interface. They can send requests straight to the API with curl or scripts, so any front-end check can be bypassed. They can send very large text, text crafted to make our cleaning code slow, or hundreds of requests at once. They can also scan the server for missing security headers, leaked versions and vulnerable dependencies.

**Which risks our design exposes:**

| Risk (§2.7) | Applies? | Why |
|---|---|---|
| **Denial of service** | **Yes, chosen** | Analysing text costs far more than sending it. We found a regex in our own cleaning code that takes ~20 s on one 160 KB request |
| **Misconfiguration and vulnerable dependencies** | **Yes, chosen** | FastAPI sets no security headers by default, and our dependencies had a known vulnerability |
| Missing rate limiting | Yes | Partly covered by the concurrency limit. Not chosen as a marked defence |
| Unsafe model loading | Low | The model files are our own and shipped in the repository, not downloaded |
| SQL injection | No | No database. Input is never stored or used to build a query |
| SSRF / Command injection | No | The back end never makes outbound requests or runs system commands |
| Unsafe file upload | No | The app accepts text only |
| Broken access control | No | No user accounts |

## References

Davis, J.C., Coghlan, C.A., Servant, F. and Lee, D. (2018) 'The impact of regular expression denial of service (ReDoS) in practice: an empirical study at the ecosystem scale', in *Proceedings of the 2018 26th ACM Joint Meeting on European Software Engineering Conference and Symposium on the Foundations of Software Engineering*. ACM, pp. 246–256.

FastAPI (2026) *FastAPI documentation*. Available at: https://fastapi.tiangolo.com (Accessed: 9 November 2026).

GitHub (2026) *GHSA-g3hv-75wg-m249: minimatch has potential denial of service via globparts amplification*. Available at: https://github.com/advisories/GHSA-g3hv-75wg-m249 (Accessed: 9 November 2026).


OWASP Foundation (2021) *OWASP Top 10: 2021*. Available at: https://owasp.org/Top10/ (Accessed: 9 November 2026).


OWASP Foundation (2026) *OWASP Secure Headers Project*. Available at: https://owasp.org/www-project-secure-headers/ (Accessed: 9 November 2026).

Pedregosa, F. et al. (2011) 'Scikit-learn: machine learning in Python', *Journal of Machine Learning Research*, 12, pp. 2825–2830.


