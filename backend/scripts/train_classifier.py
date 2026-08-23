"""
VoiceShield AI - Prototype classifier training script

Trains a small scikit-learn classifier (RandomForest) on handcrafted audio
features to distinguish genuine vs synthetic speech samples, using the
folders:

    data/genuine/    (label 0 - real human speech)
    data/synthetic/  (label 1 - AI-generated / cloned speech)

This is explicitly a PROTOTYPE classifier trained on a small sample set.
It will not generalize the way a production deepfake detector trained on
tens of thousands of hours of audio would. Report metrics honestly.

Usage (from backend/ directory):
    python scripts/train_classifier.py

Requires at least a handful of files in each folder. If you have very few
samples, the script still runs but warns loudly about unreliable metrics.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
)

from app.config import BASE_DIR, MODEL_DIR
from app.services.audio_processor import load_and_preprocess, feature_vector, AudioProcessingError

DATA_DIR = BASE_DIR.parent / "data"
GENUINE_DIR = DATA_DIR / "genuine"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
OUT_PATH = Path(MODEL_DIR) / "authenticity_classifier.joblib"

AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}


def _collect(folder: Path, label: int):
    X, y, skipped = [], [], []
    if not folder.exists():
        return X, y, skipped
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() not in AUDIO_EXTS:
            continue
        try:
            features = load_and_preprocess(str(f))
            X.append(feature_vector(features))
            y.append(label)
        except AudioProcessingError as exc:
            skipped.append((f.name, str(exc)))
    return X, y, skipped


def main():
    print("Collecting genuine samples from", GENUINE_DIR)
    Xg, yg, skipped_g = _collect(GENUINE_DIR, label=0)
    print(f"  -> {len(Xg)} usable, {len(skipped_g)} skipped")

    print("Collecting synthetic samples from", SYNTHETIC_DIR)
    Xs, ys, skipped_s = _collect(SYNTHETIC_DIR, label=1)
    print(f"  -> {len(Xs)} usable, {len(skipped_s)} skipped")

    X = np.array(Xg + Xs)
    y = np.array(yg + ys)

    if len(X) < 6:
        print(
            "\n[WARNING] Fewer than 6 total samples found. Training will still "
            "run, but the resulting classifier is not meaningful -- use DEMO "
            "MODE for reliable demonstrations until you add more sample audio "
            "to data/genuine/ and data/synthetic/."
        )
    if len(set(y.tolist())) < 2:
        print(
            "\n[ERROR] Need samples in BOTH data/genuine/ and data/synthetic/ "
            "to train a classifier. Aborting."
        )
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y if len(X) >= 8 else None
    )

    clf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("\n--- PROTOTYPE EVALUATION (small sample set -- not real-world performance) ---")
    print("Accuracy: ", round(accuracy_score(y_test, y_pred), 3))
    print("Precision:", round(precision_score(y_test, y_pred, zero_division=0), 3))
    print("Recall:   ", round(recall_score(y_test, y_pred, zero_division=0), 3))
    print("F1:       ", round(f1_score(y_test, y_pred, zero_division=0), 3))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

    Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, OUT_PATH)
    print(f"\nSaved prototype classifier to {OUT_PATH}")
    print("Restart the backend to pick it up (VOICESHIELD_MODE=real or auto).")


if __name__ == "__main__":
    main()
