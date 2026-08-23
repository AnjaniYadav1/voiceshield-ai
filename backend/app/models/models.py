"""
VoiceShield AI - ORM models

Tables: users, trusted_speakers, voice_analyses, detection_events

Note on privacy: trusted_speakers stores a numeric embedding derived from a
reference recording, not the raw audio itself. Embeddings are sensitive
biometric-derived data -- treat the embeddings table/file with the same care
as any other biometric template (restrict access, do not expose via public
API, consider encryption-at-rest in a non-MVP deployment).
"""
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TrustedSpeaker(Base):
    __tablename__ = "trusted_speakers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    speaker_id = Column(String(64), unique=True, index=True, nullable=False)
    embedding = Column(JSON, nullable=False)   # list[float], NOT raw audio
    embedding_dim = Column(Integer, nullable=False)
    embedding_method = Column(String(64), nullable=False)  # e.g. "mfcc_mean_v1"
    created_at = Column(DateTime, default=datetime.utcnow)

    analyses = relationship("VoiceAnalysis", back_populates="speaker")


class VoiceAnalysis(Base):
    __tablename__ = "voice_analyses"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    speaker_id = Column(String(64), ForeignKey("trusted_speakers.speaker_id"), nullable=True)
    filename = Column(String(256), nullable=False)
    duration = Column(Float, nullable=False)

    ai_probability = Column(Float, nullable=False)
    speaker_similarity = Column(Float, nullable=True)   # null if no reference speaker
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(16), nullable=False)      # LOW / MEDIUM / HIGH
    classification = Column(String(32), nullable=False)  # REAL / SUSPICIOUS / LIKELY_AI_GENERATED

    model_mode = Column(String(32), nullable=False)       # pretrained / prototype_classifier / demo
    signals = Column(JSON, nullable=False, default=list)
    recommendation = Column(Text, nullable=False)

    speaker = relationship("TrustedSpeaker", back_populates="analyses")
    events = relationship("DetectionEvent", back_populates="analysis")


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("voice_analyses.id"), nullable=False)
    event_type = Column(String(64), nullable=False)   # e.g. "high_risk_flagged"
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)

    analysis = relationship("VoiceAnalysis", back_populates="events")
