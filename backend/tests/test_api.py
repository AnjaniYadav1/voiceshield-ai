"""
API-level tests using FastAPI's TestClient. Runs in DEMO MODE (forced via
the VOICESHIELD_MODE env var, set before the app is imported) so tests never
depend on librosa/model availability.
"""
import io
import os

os.environ["VOICESHIELD_MODE"] = "demo"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _fake_wav_bytes():
    # Minimal content is fine -- demo mode doesn't need real audio.
    return io.BytesIO(b"RIFF....WAVEfmt fake content for demo mode")


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["mode"] == "demo"


def test_analyze_genuine_filename_gives_low_risk():
    files = {"file": ("genuine_sample.wav", _fake_wav_bytes(), "audio/wav")}
    resp = client.post("/api/analyze", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["classification"] == "REAL"
    assert data["risk_level"] == "LOW"
    assert data["model_mode"] == "demo"


def test_analyze_synthetic_filename_gives_high_risk():
    files = {"file": ("synthetic_clone_sample.wav", _fake_wav_bytes(), "audio/wav")}
    resp = client.post("/api/analyze", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["classification"] == "LIKELY_AI_GENERATED"
    assert data["risk_level"] == "HIGH"


def test_analyze_rejects_bad_extension():
    files = {"file": ("malware.exe", io.BytesIO(b"not audio"), "application/octet-stream")}
    resp = client.post("/api/analyze", files=files)
    assert resp.status_code == 400


def test_analyze_rejects_empty_file():
    files = {"file": ("empty.wav", io.BytesIO(b""), "audio/wav")}
    resp = client.post("/api/analyze", files=files)
    assert resp.status_code == 400


def test_statistics_endpoint_after_analyses():
    resp = client.get("/api/statistics")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_analyses"] >= 2
    assert data["mode"] == "demo"


def test_delete_nonexistent_analysis():
    resp = client.delete("/api/analyses/999999")
    assert resp.status_code == 404


def test_speaker_list_empty_or_present():
    resp = client.get("/api/speakers")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
