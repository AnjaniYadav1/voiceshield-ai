"""
Tests for audio preprocessing edge cases:
empty file, unsupported format, very short/long audio, corrupted audio.
"""
import numpy as np
import soundfile as sf
import pytest

from app.services.audio_processor import load_and_preprocess, AudioProcessingError


def _write_wav(path, duration_seconds, sr=16000, freq=220.0):
    t = np.linspace(0, duration_seconds, int(sr * duration_seconds), endpoint=False)
    y = 0.3 * np.sin(2 * np.pi * freq * t)
    sf.write(str(path), y, sr)


def test_normal_audio_loads(tmp_path):
    p = tmp_path / "tone.wav"
    _write_wav(p, duration_seconds=2.0)
    features = load_and_preprocess(str(p))
    assert 1.5 <= features.duration <= 2.5
    assert features.sample_rate == 16000
    assert features.mfcc_mean.shape[0] == 20


def test_too_short_audio_rejected(tmp_path):
    p = tmp_path / "short.wav"
    _write_wav(p, duration_seconds=0.1)
    with pytest.raises(AudioProcessingError):
        load_and_preprocess(str(p))


def test_empty_file_rejected(tmp_path):
    p = tmp_path / "empty.wav"
    p.write_bytes(b"")
    with pytest.raises(AudioProcessingError):
        load_and_preprocess(str(p))


def test_corrupted_file_rejected(tmp_path):
    p = tmp_path / "corrupt.wav"
    p.write_bytes(b"this is not a real wav file at all")
    with pytest.raises(AudioProcessingError):
        load_and_preprocess(str(p))


def test_long_audio_rejected(tmp_path):
    p = tmp_path / "long.wav"
    _write_wav(p, duration_seconds=125.0)
    with pytest.raises(AudioProcessingError):
        load_and_preprocess(str(p))
