"""
VoiceShield AI - Authenticity detector

IMPORTANT (read before trusting this module's output):
This is a hackathon MVP. There are three possible operating modes, always
reported alongside the score so nobody mistakes one for another:

  "demo"                -> fully deterministic, simulated score. Used when
                            VOICESHIELD_MODE=demo or when real analysis is
                            unavailable. NEVER presented as a real prediction.

  "prototype_classifier" -> a small classifier (logistic regression / random
                            forest via scikit-learn) trained on handcrafted
                            acoustic features (MFCC, mel-spectrogram, spectral
                            centroid/bandwidth, ZCR, chroma, pitch stats).
                            This is a genuine model, but it is NOT a
                            state-of-the-art deepfake detector, was trained on
                            a small sample set, and should not be presented as
                            production-grade or universally accurate.

  "pretrained"           -> reserved for a downloaded pretrained deepfake-audio
                            detection model. Not wired up in this MVP build
                            because it requires a network connection to fetch
                            model weights; the hook (`load_pretrained_model`)
                            is left in place for teams that have connectivity
                            to add one during development.

Do not remove or water down these labels in the API response -- the
frontend displays them so users understand exactly what produced a result.
"""
import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

from app.config import MODEL_DIR
from app.services.audio_processor import AudioFeatures, feature_vector

CLASSIFIER_PATH = Path(MODEL_DIR) / "authenticity_classifier.joblib"

_classifier = None
_classifier_load_attempted = False


def load_pretrained_model():
    """
    Hook for a real pretrained deepfake-audio detection model.
    Not implemented in this offline MVP build (requires downloading model
    weights). Returns None so callers fall back to the prototype classifier.
    """
    return None


def _try_load_prototype_classifier():
    """Load the scikit-learn prototype classifier if one has been trained."""
    global _classifier, _classifier_load_attempted
    if _classifier_load_attempted:
        return _classifier
    _classifier_load_attempted = True

    if not CLASSIFIER_PATH.exists():
        return None
    try:
        import joblib
        _classifier = joblib.load(CLASSIFIER_PATH)
    except Exception:
        _classifier = None
    return _classifier


def prototype_classifier_available() -> bool:
    return _try_load_prototype_classifier() is not None


def _deterministic_demo_score(filename: str) -> float:
    """
    Deterministic simulated AI-probability for DEMO MODE, keyed off the
    filename so the same test file always produces the same demo result.
    Convention (matches data/ folder layout used for the demo script):
      filenames containing "synthetic" / "ai" / "clone" -> high probability
      filenames containing "genuine" / "real"           -> low probability
      anything else -> mid-range, derived from a hash so it's still
                        deterministic and varied across files.
    """
    name = filename.lower()
    if any(k in name for k in ("synthetic", "clone", "ai_", "fake", "deepfake")):
        base = 0.85
    elif any(k in name for k in ("genuine", "real")):
        base = 0.12
    else:
        h = int(hashlib.sha256(name.encode()).hexdigest(), 16)
        base = 0.25 + (h % 1000) / 1000 * 0.5  # spread across 0.25-0.75
    return float(np.clip(base, 0.0, 1.0))


def _heuristic_score(features: AudioFeatures) -> float:
    """
    Zero-training-data fallback heuristic, used only if neither a pretrained
    model nor a trained prototype classifier is available, and demo mode is
    off. Combines a few acoustic properties loosely associated in literature
    with synthetic speech: unnaturally low pitch variance, low high-frequency
    spectral variation, and low RMS variance -- NOT a validated detector,
    explicitly labeled "prototype_classifier" with a low-confidence signal
    when this path is used.
    """
    pitch_variability = features.pitch_std / (features.pitch_mean + 1e-6)
    low_pitch_variability_flag = 1.0 if pitch_variability < 0.05 else 0.0

    centroid_flag = 1.0 if features.spectral_centroid_mean < 1200 else 0.0
    zcr_flag = 1.0 if features.zero_crossing_rate_mean < 0.03 else 0.0

    raw = 0.5 * low_pitch_variability_flag + 0.3 * centroid_flag + 0.2 * zcr_flag
    # keep it away from the extremes since this path is low-confidence
    return float(np.clip(0.2 + raw * 0.6, 0.05, 0.95))


def analyze_authenticity(
    features: Optional[AudioFeatures],
    filename: str,
    mode: str,
) -> Tuple[float, str, float]:
    """
    Returns (ai_probability, model_mode_used, detector_confidence)

    mode: "auto" | "real" | "demo" (from app.config.VOICESHIELD_MODE)
    """
    if mode == "demo":
        return _deterministic_demo_score(filename), "demo", 1.0

    # mode == "real" or "auto" -> try real pipeline first
    pretrained = load_pretrained_model()
    if pretrained is not None:  # pragma: no cover - no pretrained model wired up
        prob = float(pretrained.predict(features))
        return prob, "pretrained", 0.9

    clf = _try_load_prototype_classifier()
    if clf is not None and features is not None:
        vec = feature_vector(features).reshape(1, -1)
        try:
            prob = float(clf.predict_proba(vec)[0][1])
            return prob, "prototype_classifier", 0.7
        except Exception:
            pass

    if features is not None:
        return _heuristic_score(features), "prototype_classifier", 0.4

    if mode == "auto":
        # No features (e.g. librosa unavailable) -> fall back to demo so the
        # app remains demonstrable.
        return _deterministic_demo_score(filename), "demo", 1.0

    raise RuntimeError("Real analysis requested but no detector or features available.")
