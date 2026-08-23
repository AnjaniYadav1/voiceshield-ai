"""
VoiceShield AI - Risk engine

Combines signals into a single, explainable risk_score and classification.
Weights and thresholds are pulled from app.config so they can be tuned
without touching this logic (and so nobody can accuse the demo of hardcoding
a fake scientific formula -- the formula is simple, visible, and configurable).
"""
from typing import List, Optional, Tuple

from app.config import (
    RISK_WEIGHTS, RISK_THRESHOLDS, CLASSIFICATION_THRESHOLDS,
    SPEAKER_MATCH_THRESHOLD,
)


def _risk_level(risk_score: float) -> str:
    if risk_score < RISK_THRESHOLDS["LOW"]:
        return "LOW"
    if risk_score < RISK_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    return "HIGH"


def _classification(ai_probability: float) -> str:
    if ai_probability < CLASSIFICATION_THRESHOLDS["REAL_MAX"]:
        return "REAL"
    if ai_probability < CLASSIFICATION_THRESHOLDS["SUSPICIOUS_MAX"]:
        return "SUSPICIOUS"
    return "LIKELY_AI_GENERATED"


def compute_risk(
    ai_probability: float,
    speaker_similarity: Optional[float],
    audio_quality_score: float,
    detector_confidence: float,
) -> Tuple[float, str, str, List[dict]]:
    """
    Returns (risk_score, risk_level, classification, signals)

    risk_score = w1*authenticity_anomaly + w2*speaker_mismatch (if available)
                 + w3*audio_quality_penalty

    If no reference speaker was supplied, the speaker_mismatch term is
    dropped and its weight is proportionally redistributed to authenticity,
    so an unverifiable speaker doesn't silently produce a lower score.
    """
    w_auth = RISK_WEIGHTS["authenticity_anomaly"]
    w_spk = RISK_WEIGHTS["speaker_mismatch"]
    w_qual = RISK_WEIGHTS["audio_quality_penalty"]

    authenticity_anomaly = ai_probability  # higher AI-probability = higher anomaly
    audio_quality_penalty = 1.0 - audio_quality_score  # poor quality -> can't trust result -> nudges risk up slightly & flags low confidence

    signals = []

    if speaker_similarity is not None:
        speaker_mismatch = 1.0 - speaker_similarity
        risk_score = (
            w_auth * authenticity_anomaly
            + w_spk * speaker_mismatch
            + w_qual * audio_quality_penalty
        )
    else:
        # redistribute speaker weight to authenticity when no reference exists
        redistributed_auth_weight = w_auth + w_spk
        risk_score = (
            redistributed_auth_weight * authenticity_anomaly
            + w_qual * audio_quality_penalty
        )
        speaker_mismatch = None

    risk_score = max(0.0, min(1.0, risk_score))
    risk_level = _risk_level(risk_score)
    classification = _classification(ai_probability)

    # ---- Explainability: build the human-readable signal list ----
    if audio_quality_score >= 0.6:
        signals.append({"label": "Audio quality sufficient for analysis", "severity": "ok"})
    else:
        signals.append({"label": "Low audio quality -- results may be less reliable", "severity": "warning"})

    if ai_probability >= CLASSIFICATION_THRESHOLDS["SUSPICIOUS_MAX"]:
        signals.append({"label": "Authenticity model indicates likely synthetic speech", "severity": "critical"})
    elif ai_probability >= CLASSIFICATION_THRESHOLDS["REAL_MAX"]:
        signals.append({"label": "Some synthetic-speech characteristics detected", "severity": "warning"})
    else:
        signals.append({"label": "No strong synthetic-speech indicators detected", "severity": "ok"})

    if speaker_similarity is not None:
        if speaker_similarity < SPEAKER_MATCH_THRESHOLD:
            signals.append({"label": "Speaker embedding mismatch vs. registered voice", "severity": "critical"})
        else:
            signals.append({"label": "Speaker embedding matches registered voice", "severity": "ok"})
    else:
        signals.append({"label": "No reference speaker registered -- identity not verified", "severity": "warning"})

    if detector_confidence < 0.5:
        signals.append({"label": "Detector confidence is low for this sample (prototype heuristic path used)", "severity": "warning"})

    recommendation = _recommendation(risk_level, speaker_similarity)

    return risk_score, risk_level, classification, signals, recommendation


def _recommendation(risk_level: str, speaker_similarity: Optional[float]) -> str:
    if risk_level == "HIGH":
        return (
            "Do not authorize sensitive actions (money transfers, password resets, "
            "OTP sharing, confidential disclosures) based on this voice interaction. "
            "Verify the speaker's identity through an independent, trusted channel "
            "before proceeding."
        )
    if risk_level == "MEDIUM":
        return (
            "Proceed with caution. Consider verifying the speaker's identity through "
            "a secondary channel before authorizing any sensitive request."
        )
    return "No significant risk indicators detected. Standard verification practices still apply."
