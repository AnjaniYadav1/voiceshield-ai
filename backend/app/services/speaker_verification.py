"""
VoiceShield AI - Speaker verification

Generates a fixed-length "voiceprint" embedding for a speaker and compares
input audio against a stored reference embedding using cosine similarity.

MODEL NOTE:
A production system would use a pretrained speaker-embedding network (e.g.
ECAPA-TDNN / x-vector style models). Those require downloading model weights,
which this offline MVP build cannot do. Instead this module uses a documented
fallback: a normalized MFCC-statistics embedding. It is a real, working
similarity measure -- genuinely more similar voices score higher -- but it is
lower-fidelity than a trained neural embedding, and is labeled as such
("mfcc_mean_v1") everywhere it is stored or reported.

Embeddings are derived biometric data. This module never persists raw
reference audio; only the embedding vector is stored in the database.
"""
from typing import Optional

import numpy as np

from app.services.audio_processor import AudioFeatures

EMBEDDING_METHOD = "mfcc_mean_v1"


def generate_embedding(features: AudioFeatures) -> list:
    """
    Build a compact voiceprint from MFCC mean/std, chroma mean, and pitch
    statistics -- features chosen because they capture vocal-tract and
    pitch characteristics that vary by speaker while being cheap to compute
    without a neural network.
    """
    vec = np.concatenate([
        features.mfcc_mean,
        features.mfcc_std,
        features.chroma_mean,
        np.array([features.pitch_mean, features.pitch_std]),
    ])
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


def cosine_similarity(a: list, b: list) -> float:
    va, vb = np.array(a), np.array(b)
    if va.shape != vb.shape:
        # Defensive: embeddings from incompatible feature-set versions
        return 0.0
    denom = (np.linalg.norm(va) * np.linalg.norm(vb))
    if denom == 0:
        return 0.0
    sim = float(np.dot(va, vb) / denom)
    # cosine similarity is in [-1, 1]; rescale to [0, 1] for a "match %" feel
    return float(np.clip((sim + 1) / 2, 0.0, 1.0))


def verify_speaker(input_embedding: list, reference_embedding: list) -> float:
    """Returns a similarity score in [0, 1], where 1.0 is a perfect match."""
    return cosine_similarity(input_embedding, reference_embedding)
