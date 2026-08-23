"""
VoiceShield AI - Configuration
All magic numbers live here so the risk engine and detectors stay configurable
and auditable, instead of hardcoding thresholds inside logic files.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Vercel's serverless filesystem is read-only everywhere except /tmp, so any
# folder we create or file we write (uploads, embeddings, the SQLite db)
# must live there when running on Vercel. Locally (uvicorn, run.bat) or on
# a normal server (Render, a VM), the project directory works fine and is
# used instead so nothing changes for that setup.
IS_VERCEL = os.getenv("VERCEL") == "1"
RUNTIME_DIR = Path("/tmp/voiceshield") if IS_VERCEL else BASE_DIR

UPLOAD_DIR = RUNTIME_DIR / "uploads"
EMBEDDINGS_DIR = RUNTIME_DIR / "embeddings"
MODEL_DIR = BASE_DIR.parent / "models"
DB_PATH = RUNTIME_DIR / "voiceshield.db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# Operating mode
# ----------------------------------------------------------------------
# "auto"  -> try REAL ML mode, fall back to DEMO automatically if models
#            or dependencies are unavailable
# "real"  -> force real feature-based pipeline (prototype classifier)
# "demo"  -> force deterministic simulated results (always works, no ML deps)
VOICESHIELD_MODE = os.getenv("VOICESHIELD_MODE", "auto")

# ----------------------------------------------------------------------
# File validation
# ----------------------------------------------------------------------
MAX_FILE_SIZE_MB = 15
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac"}
TARGET_SAMPLE_RATE = 16000
MIN_DURATION_SECONDS = 0.5
MAX_DURATION_SECONDS = 120

# ----------------------------------------------------------------------
# Risk engine weights (must sum to <= 1.0 across the primary three;
# audio-quality is a penalty modifier, not a primary weight)
# ----------------------------------------------------------------------
RISK_WEIGHTS = {
    "authenticity_anomaly": 0.5,   # weight on (1 - authenticity) i.e. AI-probability
    "speaker_mismatch": 0.35,      # weight on (1 - speaker_similarity), only if a
                                     # reference speaker was supplied
    "audio_quality_penalty": 0.15,  # weight on low-quality / low-confidence audio
}

# Risk level thresholds (on a 0-1 risk_score)
RISK_THRESHOLDS = {
    "LOW": 0.35,
    "MEDIUM": 0.65,
    # anything >= MEDIUM threshold and above -> HIGH
}

# Classification thresholds (on ai_probability, independent of speaker match)
CLASSIFICATION_THRESHOLDS = {
    "REAL_MAX": 0.35,          # ai_probability below this -> likely REAL
    "SUSPICIOUS_MAX": 0.70,     # below this (and above REAL_MAX) -> SUSPICIOUS
    # >= SUSPICIOUS_MAX -> LIKELY AI-GENERATED
}

# Speaker verification similarity threshold below which we flag a mismatch
SPEAKER_MATCH_THRESHOLD = 0.55

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
