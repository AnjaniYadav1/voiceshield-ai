"""
Vercel serverless entrypoint for the VoiceShield AI backend.

Vercel's Python runtime looks for a FastAPI/ASGI `app` instance in files
under api/. This file imports the real app from backend/app/main.py
unchanged -- we just need backend/ on sys.path first, since the existing
code uses "from app.config import ..." style imports written for running
via `uvicorn app.main:app` from inside the backend/ folder.
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402  (Vercel serves this ASGI app)
