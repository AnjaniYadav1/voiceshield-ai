"""
VoiceShield AI - Audio preprocessing

Responsible for:
 - loading arbitrary uploaded audio into a consistent numpy waveform
 - resampling to a fixed sample rate
 - trimming silence / unusable sections
 - computing duration
 - extracting the acoustic feature set used by the authenticity detector
   and the fallback speaker embedding

This module never raises raw stack traces to the caller -- it raises
AudioProcessingError with a clean, user-facing message, which the API
layer converts into an HTTP error response.
"""
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from app.config import TARGET_SAMPLE_RATE, MIN_DURATION_SECONDS, MAX_DURATION_SECONDS

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only if librosa missing
    LIBROSA_AVAILABLE = False


class AudioProcessingError(Exception):
    """Raised for any audio that cannot be safely analyzed."""


@dataclass
class AudioFeatures:
    duration: float
    sample_rate: int
    mfcc_mean: np.ndarray
    mfcc_std: np.ndarray
    mel_mean: np.ndarray
    spectral_centroid_mean: float
    spectral_bandwidth_mean: float
    zero_crossing_rate_mean: float
    chroma_mean: np.ndarray
    pitch_mean: float
    pitch_std: float
    rms_mean: float
    quality_score: float  # 0-1, crude audio-quality proxy (SNR-ish heuristic)
    waveform_preview: list = field(default_factory=list)  # downsampled, for UI


def _crude_quality_score(y: np.ndarray, sr: int) -> float:
    """
    Very small heuristic proxy for "is this audio clean enough to trust the
    analysis". Not a real SNR estimator -- documented as a heuristic only.
    Combines: non-silence ratio, dynamic range, clipping ratio.
    """
    if y.size == 0:
        return 0.0
    abs_y = np.abs(y)
    non_silence_ratio = float(np.mean(abs_y > 0.01))
    dynamic_range = float(np.percentile(abs_y, 95) - np.percentile(abs_y, 5))
    clipping_ratio = float(np.mean(abs_y > 0.98))

    score = 0.5 * non_silence_ratio + 0.5 * min(dynamic_range * 4, 1.0)
    score -= clipping_ratio  # penalize heavy clipping
    return float(np.clip(score, 0.0, 1.0))


def load_and_preprocess(file_path: str) -> AudioFeatures:
    """
    Load an audio file from disk, normalize sample rate, trim silence,
    validate duration bounds, and extract the feature set.
    """
    if not LIBROSA_AVAILABLE:
        raise AudioProcessingError(
            "Audio processing library (librosa) is not available on this "
            "server. Run the backend in DEMO MODE, or install requirements.txt."
        )

    try:
        y, sr = librosa.load(file_path, sr=TARGET_SAMPLE_RATE, mono=True)
    except Exception as exc:
        raise AudioProcessingError(
            f"Could not read audio file. It may be corrupted or in an "
            f"unsupported format. ({type(exc).__name__})"
        ) from exc

    if y is None or y.size == 0:
        raise AudioProcessingError("Uploaded audio contains no usable audio data.")

    # Trim leading/trailing silence (unusable sections)
    y_trimmed, _ = librosa.effects.trim(y, top_db=30)
    if y_trimmed.size > 0:
        y = y_trimmed

    duration = float(len(y) / sr)

    if duration < MIN_DURATION_SECONDS:
        raise AudioProcessingError(
            f"Audio is too short to analyze reliably "
            f"(minimum {MIN_DURATION_SECONDS}s required)."
        )
    if duration > MAX_DURATION_SECONDS:
        raise AudioProcessingError(
            f"Audio is too long for this MVP "
            f"(maximum {MAX_DURATION_SECONDS}s supported)."
        )

    try:
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
        mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        zcr = librosa.feature.zero_crossing_rate(y)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        rms = librosa.feature.rms(y=y)

        f0, voiced_flag, _ = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7")
        )
        voiced_f0 = f0[voiced_flag] if f0 is not None else np.array([])
        pitch_mean = float(np.nanmean(voiced_f0)) if voiced_f0.size > 0 else 0.0
        pitch_std = float(np.nanstd(voiced_f0)) if voiced_f0.size > 0 else 0.0

    except Exception as exc:
        raise AudioProcessingError(
            f"Feature extraction failed on this audio sample. "
            f"({type(exc).__name__})"
        ) from exc

    # Downsample waveform for frontend preview (~400 points max)
    step = max(1, len(y) // 400)
    waveform_preview = y[::step].tolist()

    return AudioFeatures(
        duration=duration,
        sample_rate=sr,
        mfcc_mean=np.mean(mfcc, axis=1),
        mfcc_std=np.std(mfcc, axis=1),
        mel_mean=np.mean(mel_db, axis=1),
        spectral_centroid_mean=float(np.mean(spectral_centroid)),
        spectral_bandwidth_mean=float(np.mean(spectral_bandwidth)),
        zero_crossing_rate_mean=float(np.mean(zcr)),
        chroma_mean=np.mean(chroma, axis=1),
        pitch_mean=pitch_mean,
        pitch_std=pitch_std,
        rms_mean=float(np.mean(rms)),
        quality_score=_crude_quality_score(y, sr),
        waveform_preview=waveform_preview,
    )


def feature_vector(features: AudioFeatures) -> np.ndarray:
    """Flatten AudioFeatures into a single numeric vector for ML models."""
    return np.concatenate([
        features.mfcc_mean,
        features.mfcc_std,
        features.mel_mean,
        features.chroma_mean,
        np.array([
            features.spectral_centroid_mean,
            features.spectral_bandwidth_mean,
            features.zero_crossing_rate_mean,
            features.pitch_mean,
            features.pitch_std,
            features.rms_mean,
        ]),
    ])
