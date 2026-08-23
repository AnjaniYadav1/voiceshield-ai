"""
VoiceShield AI - API routes

Endpoints:
  GET    /api/health
  POST   /api/analyze
  POST   /api/analyze/live
  POST   /api/speakers/register
  GET    /api/speakers
  GET    /api/analyses
  GET    /api/analyses/{id}
  DELETE /api/analyses/{id}
  GET    /api/statistics
"""
import os
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import (
    UPLOAD_DIR, MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS, VOICESHIELD_MODE,
)
from app.database import get_db
from app.models import models as db_models
from app.schemas import schemas
from app.services.audio_processor import load_and_preprocess, AudioProcessingError
from app.services import authenticity_detector, speaker_verification, risk_engine

router = APIRouter(prefix="/api")


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _sanitize_filename(filename: str) -> str:
    """Strip paths and keep only a safe basename to prevent path traversal."""
    name = os.path.basename(filename or "upload")
    name = "".join(c for c in name if c.isalnum() or c in "._-")
    return name or "upload"


def _validate_and_save(upload: UploadFile) -> Path:
    ext = Path(upload.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    contents = upload.file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f} MB). Max is {MAX_FILE_SIZE_MB} MB.",
        )
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    safe_name = _sanitize_filename(upload.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    dest = UPLOAD_DIR / unique_name
    with open(dest, "wb") as f:
        f.write(contents)
    return dest


def _run_pipeline(
    file_path: Path,
    original_filename: str,
    speaker_id: Optional[str],
    db: Session,
) -> schemas.AnalysisResult:
    features = None
    quality_score = 0.5
    duration = 0.0

    try:
        features = load_and_preprocess(str(file_path))
        quality_score = features.quality_score
        duration = features.duration
    except AudioProcessingError as exc:
        if VOICESHIELD_MODE == "demo":
            # demo mode tolerates unreadable audio -- we never actually need
            # real features to produce the simulated result
            duration = 1.0
        else:
            raise HTTPException(status_code=422, detail=str(exc))

    ai_probability, model_mode, confidence = authenticity_detector.analyze_authenticity(
        features, original_filename, VOICESHIELD_MODE
    )

    speaker_similarity = None
    if speaker_id:
        speaker = db.query(db_models.TrustedSpeaker).filter_by(speaker_id=speaker_id).first()
        if not speaker:
            raise HTTPException(status_code=404, detail=f"Unknown speaker_id '{speaker_id}'.")
        if model_mode == "demo" or features is None:
            # deterministic demo similarity, still informative for the walkthrough
            speaker_similarity = 0.88 if "genuine" in original_filename.lower() else 0.27
        else:
            input_embedding = speaker_verification.generate_embedding(features)
            speaker_similarity = speaker_verification.verify_speaker(
                input_embedding, speaker.embedding
            )

    risk_score, risk_level, classification, signals, recommendation = risk_engine.compute_risk(
        ai_probability=ai_probability,
        speaker_similarity=speaker_similarity,
        audio_quality_score=quality_score,
        detector_confidence=confidence,
    )

    record = db_models.VoiceAnalysis(
        speaker_id=speaker_id,
        filename=original_filename,
        duration=duration,
        ai_probability=ai_probability,
        speaker_similarity=speaker_similarity,
        risk_score=risk_score,
        risk_level=risk_level,
        classification=classification,
        model_mode=model_mode,
        signals=signals,
        recommendation=recommendation,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    if risk_level == "HIGH":
        event = db_models.DetectionEvent(
            analysis_id=record.id,
            event_type="high_risk_flagged",
            details={"risk_score": risk_score, "classification": classification},
        )
        db.add(event)
        db.commit()

    return schemas.AnalysisResult(
        id=record.id,
        timestamp=record.timestamp,
        filename=record.filename,
        duration=record.duration,
        speaker_id=record.speaker_id,
        classification=record.classification,
        ai_probability=record.ai_probability,
        speaker_match=record.speaker_similarity,
        risk_score=record.risk_score,
        risk_level=record.risk_level,
        model_mode=record.model_mode,
        signals=record.signals,
        recommendation=record.recommendation,
    )


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@router.get("/health", response_model=schemas.HealthOut)
def health():
    return schemas.HealthOut(
        status="ok",
        mode=VOICESHIELD_MODE,
        detector_available=authenticity_detector.prototype_classifier_available(),
        speaker_verification_available=True,
    )


@router.post("/analyze", response_model=schemas.AnalysisResult)
def analyze(
    file: UploadFile = File(...),
    speaker_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    dest = _validate_and_save(file)
    try:
        return _run_pipeline(dest, file.filename or "upload", speaker_id, db)
    except HTTPException:
        raise
    except Exception as exc:
        # Never leak stack traces to the client
        raise HTTPException(status_code=500, detail="Analysis failed unexpectedly.") from exc


@router.post("/analyze/live", response_model=schemas.AnalysisResult)
def analyze_live(
    file: UploadFile = File(...),
    speaker_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Near-real-time prototype endpoint: accepts a recorded audio chunk/blob
    from the browser (MediaRecorder) and runs the same pipeline as /analyze.
    This is chunked near-real-time analysis, not true continuous streaming
    inference -- labeled as such in the frontend UI.
    """
    dest = _validate_and_save(file)
    try:
        return _run_pipeline(dest, file.filename or "live_recording.webm", speaker_id, db)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Live analysis failed unexpectedly.") from exc


@router.post("/speakers/register", response_model=schemas.TrustedSpeakerOut)
def register_speaker(
    name: str = Form(...),
    speaker_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    existing = db.query(db_models.TrustedSpeaker).filter_by(speaker_id=speaker_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"speaker_id '{speaker_id}' already registered.")

    dest = _validate_and_save(file)
    try:
        features = load_and_preprocess(str(dest))
    except AudioProcessingError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        # We only need the embedding, not the raw reference audio long-term.
        try:
            os.remove(dest)
        except OSError:
            pass

    embedding = speaker_verification.generate_embedding(features)

    speaker = db_models.TrustedSpeaker(
        name=name,
        speaker_id=speaker_id,
        embedding=embedding,
        embedding_dim=len(embedding),
        embedding_method=speaker_verification.EMBEDDING_METHOD,
    )
    db.add(speaker)
    db.commit()
    db.refresh(speaker)
    return speaker


@router.get("/speakers", response_model=List[schemas.TrustedSpeakerOut])
def list_speakers(db: Session = Depends(get_db)):
    return db.query(db_models.TrustedSpeaker).order_by(db_models.TrustedSpeaker.created_at.desc()).all()


@router.get("/analyses", response_model=List[schemas.AnalysisResult])
def list_analyses(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    rows = (
        db.query(db_models.VoiceAnalysis)
        .order_by(db_models.VoiceAnalysis.timestamp.desc())
        .offset(offset)
        .limit(min(limit, 200))
        .all()
    )
    return [
        schemas.AnalysisResult(
            id=r.id, timestamp=r.timestamp, filename=r.filename, duration=r.duration,
            speaker_id=r.speaker_id, classification=r.classification,
            ai_probability=r.ai_probability, speaker_match=r.speaker_similarity,
            risk_score=r.risk_score, risk_level=r.risk_level, model_mode=r.model_mode,
            signals=r.signals, recommendation=r.recommendation,
        )
        for r in rows
    ]


@router.get("/analyses/{analysis_id}", response_model=schemas.AnalysisResult)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    r = db.query(db_models.VoiceAnalysis).filter_by(id=analysis_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return schemas.AnalysisResult(
        id=r.id, timestamp=r.timestamp, filename=r.filename, duration=r.duration,
        speaker_id=r.speaker_id, classification=r.classification,
        ai_probability=r.ai_probability, speaker_match=r.speaker_similarity,
        risk_score=r.risk_score, risk_level=r.risk_level, model_mode=r.model_mode,
        signals=r.signals, recommendation=r.recommendation,
    )


@router.delete("/analyses/{analysis_id}")
def delete_analysis(analysis_id: int, db: Session = Depends(get_db)):
    r = db.query(db_models.VoiceAnalysis).filter_by(id=analysis_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    db.query(db_models.DetectionEvent).filter_by(analysis_id=analysis_id).delete()
    db.delete(r)
    db.commit()
    return {"deleted": analysis_id}


@router.get("/statistics", response_model=schemas.StatisticsOut)
def statistics(db: Session = Depends(get_db)):
    total = db.query(func.count(db_models.VoiceAnalysis.id)).scalar() or 0
    safe = db.query(func.count(db_models.VoiceAnalysis.id)).filter(
        db_models.VoiceAnalysis.classification == "REAL"
    ).scalar() or 0
    suspicious = db.query(func.count(db_models.VoiceAnalysis.id)).filter(
        db_models.VoiceAnalysis.classification == "SUSPICIOUS"
    ).scalar() or 0
    high_risk = db.query(func.count(db_models.VoiceAnalysis.id)).filter(
        db_models.VoiceAnalysis.risk_level == "HIGH"
    ).scalar() or 0
    avg_risk = db.query(func.avg(db_models.VoiceAnalysis.risk_score)).scalar() or 0.0

    dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for level, count in (
        db.query(db_models.VoiceAnalysis.risk_level, func.count(db_models.VoiceAnalysis.id))
        .group_by(db_models.VoiceAnalysis.risk_level)
        .all()
    ):
        dist[level] = count

    return schemas.StatisticsOut(
        total_analyses=total,
        safe_voices=safe,
        suspicious_voices=suspicious,
        high_risk_attempts=high_risk,
        average_risk_score=float(avg_risk),
        risk_distribution=dist,
        mode=VOICESHIELD_MODE,
    )
