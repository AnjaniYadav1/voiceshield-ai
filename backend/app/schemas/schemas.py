"""
VoiceShield AI - Pydantic schemas
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SignalItem(BaseModel):
    label: str
    severity: str  # "ok" | "warning" | "critical"


class AnalysisResult(BaseModel):
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    filename: str
    duration: float
    speaker_id: Optional[str] = None

    classification: str          # REAL / SUSPICIOUS / LIKELY_AI_GENERATED
    ai_probability: float = Field(..., ge=0, le=1)
    speaker_match: Optional[float] = Field(None, ge=0, le=1)
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: str               # LOW / MEDIUM / HIGH

    model_mode: str               # pretrained / prototype_classifier / demo
    signals: List[SignalItem]
    recommendation: str

    class Config:
        from_attributes = True


class TrustedSpeakerCreate(BaseModel):
    name: str
    speaker_id: str


class TrustedSpeakerOut(BaseModel):
    id: int
    name: str
    speaker_id: str
    embedding_method: str
    embedding_dim: int
    created_at: datetime

    class Config:
        from_attributes = True


class StatisticsOut(BaseModel):
    total_analyses: int
    safe_voices: int
    suspicious_voices: int
    high_risk_attempts: int
    average_risk_score: float
    risk_distribution: dict
    mode: str


class HealthOut(BaseModel):
    status: str
    mode: str
    detector_available: bool
    speaker_verification_available: bool
