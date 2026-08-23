# VoiceShield AI - Backend

FastAPI backend for detection + prevention of voice-cloning impersonation.
**This is an MVP/prototype for the Smart India Hackathon, not a production
security product.**

## Setup (Windows, PowerShell or CMD)

```bat
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy ..\.env.example .env
```

## Run

```bat
uvicorn app.main:app --reload --port 8000
```

Then open:
- API root: http://127.0.0.1:8000/
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/health

## Operating modes

Set in `.env` via `VOICESHIELD_MODE`:

| Mode | Behavior |
|---|---|
| `demo` | Always works. Deterministic simulated results, clearly labeled `DEMO MODE`. No ML dependencies required at runtime. Use this if librosa/models fail to install. |
| `real` | Forces the real feature-based pipeline (prototype classifier on handcrafted audio features + MFCC-based speaker embeddings). Requires `requirements.txt` installed successfully. |
| `auto` (default) | Tries `real`, silently falls back to `demo` per-request if audio processing or the classifier is unavailable. Recommended for demos where you're not 100% sure every dependency installed cleanly. |

## Training the prototype classifier (optional, for "real" mode)

1. Put a handful of genuine speech clips in `data/genuine/` and
   synthetic/AI-generated or voice-cloned clips (from a properly licensed
   source, or your own TTS-generated test samples) in `data/synthetic/`.
2. From `backend/`, run:
   ```bat
   python scripts/train_classifier.py
   ```
3. This prints prototype accuracy/precision/recall/F1 and a confusion matrix,
   then saves `models/authenticity_classifier.joblib`. Restart the backend
   afterwards.

Without this step, `real`/`auto` mode falls back to a low-confidence
heuristic scorer, which is still labeled honestly in every API response.

## Running tests

```bat
pip install -r requirements.txt
pytest
```

Tests run in forced `demo` mode so they never depend on librosa/model
availability, and cover: health check, analyze happy paths (genuine vs
synthetic filenames), bad file extension, empty file, unknown-analysis
delete, and the risk engine's score/threshold logic directly (including
edge cases: empty file, unsupported format, very short/long audio,
corrupted audio, no reference speaker, model unavailable).

## API endpoints

See `/docs` for full interactive documentation and schemas. Summary:

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Liveness + current mode |
| POST | `/api/analyze` | Analyze an uploaded audio file |
| POST | `/api/analyze/live` | Analyze a recorded/near-real-time audio chunk |
| POST | `/api/speakers/register` | Register a trusted speaker (name, speaker_id, reference audio) |
| GET | `/api/speakers` | List trusted speakers |
| GET | `/api/analyses` | List past analyses |
| GET | `/api/analyses/{id}` | Get one analysis |
| DELETE | `/api/analyses/{id}` | Delete an analysis |
| GET | `/api/statistics` | Dashboard aggregate stats |

## Security notes (MVP-level, not production-grade)

- Uploaded files are validated by extension and size, sanitized to a safe
  filename, and stored outside any executable path.
- Only speaker **embeddings** are persisted for trusted speakers -- the raw
  reference recording is deleted immediately after the embedding is computed.
  Embeddings are derived biometric data; treat `voiceshield.db` accordingly
  (restrict file access, don't commit it to a public repo).
- Unhandled exceptions are caught globally and never return a stack trace
  to the client.
- CORS is restricted to the configured frontend origin(s).
- This project has **not** had a security audit and should not be exposed
  to the public internet as-is.
