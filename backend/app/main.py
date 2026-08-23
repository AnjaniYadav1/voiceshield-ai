"""
VoiceShield AI - FastAPI application entrypoint

Run with (from backend/ directory):
    uvicorn app.main:app --reload --port 8000
"""
import logging
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, VOICESHIELD_MODE
from app.database import init_db
from app.api.routes import router as api_router

# frontend/dist, produced by `npm run build` inside frontend/
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voiceshield")

app = FastAPI(
    title="VoiceShield AI",
    description="Detect. Verify. Prevent Voice Impersonation. (MVP / Prototype)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("VoiceShield AI backend started in mode=%s", VOICESHIELD_MODE)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never expose stack traces to the client
    logger.exception("Unhandled error on %s", request.url)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(api_router)


if FRONTEND_DIST.exists():
    # Combined mode: the built React app lives in frontend/dist/. FastAPI
    # serves its hashed asset files directly, and falls back to index.html
    # for any other path so React Router's client-side routes (e.g. /history,
    # /analytics) work when the browser is pointed straight at them.
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/") or full_path == "docs" or full_path == "openapi.json":
            raise HTTPException(status_code=404)
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")

    logger.info("Serving built frontend from %s", FRONTEND_DIST)
else:
    @app.get("/")
    def root():
        return {
            "name": "VoiceShield AI",
            "tagline": "Detect. Verify. Prevent Voice Impersonation.",
            "docs": "/docs",
            "mode": VOICESHIELD_MODE,
            "status": "This is an MVP / prototype -- not a production security product.",
            "note": (
                "Frontend build not found at frontend/dist. Run `npm run build` "
                "inside frontend/ and restart the backend to serve the app from "
                "this same address, or run `npm run dev` separately for "
                "development mode."
            ),
        }
