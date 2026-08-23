"""
Tests for the risk engine: score ranges, level thresholds, and behavior
when no reference speaker is available.
"""
from app.services.risk_engine import compute_risk


def test_low_risk_genuine_case():
    risk_score, risk_level, classification, signals, rec = compute_risk(
        ai_probability=0.05,
        speaker_similarity=0.95,
        audio_quality_score=0.9,
        detector_confidence=0.9,
    )
    assert risk_level == "LOW"
    assert classification == "REAL"
    assert 0.0 <= risk_score <= 1.0


def test_high_risk_impersonation_case():
    risk_score, risk_level, classification, signals, rec = compute_risk(
        ai_probability=0.94,
        speaker_similarity=0.31,
        audio_quality_score=0.8,
        detector_confidence=0.9,
    )
    assert risk_level == "HIGH"
    assert classification == "LIKELY_AI_GENERATED"
    assert any(s["severity"] == "critical" for s in signals)
    assert "do not authorize" in rec.lower() or "verify" in rec.lower()


def test_no_reference_speaker_still_scores():
    risk_score, risk_level, classification, signals, rec = compute_risk(
        ai_probability=0.5,
        speaker_similarity=None,
        audio_quality_score=0.7,
        detector_confidence=0.8,
    )
    assert 0.0 <= risk_score <= 1.0
    assert any("no reference speaker" in s["label"].lower() for s in signals)


def test_risk_score_always_bounded():
    for ai_prob in (0.0, 0.5, 1.0):
        for sim in (0.0, 0.5, 1.0, None):
            for qual in (0.0, 0.5, 1.0):
                score, level, cls, sig, rec = compute_risk(ai_prob, sim, qual, 0.7)
                assert 0.0 <= score <= 1.0
                assert level in ("LOW", "MEDIUM", "HIGH")
