# VoiceShield AI — SIH Presentation Content

**Tagline:** Detect. Verify. Prevent Voice Impersonation.

---

## 1. Problem Statement

AI voice-cloning tools can now reproduce a person's voice convincingly from
just a few seconds of reference audio. Attackers are using cloned voices in
phone and voice-message scams — impersonating relatives, executives, or
officials to request money transfers, OTPs, or sensitive information. There
is no widely deployed, easy-to-use tool that lets an ordinary person or
organization check, in real time, whether a voice they're hearing might be
synthetic or doesn't match the person it claims to be.

## 2. Problem Impact

- Voice-cloning scams (including "family emergency" calls and executive
  impersonation / vishing fraud) have been reported with rising frequency
  as voice-cloning tools become cheaper and more accessible.
- Financial fraud, corporate fraud (fake CFO/CEO voice instructions), and
  emotional manipulation of vulnerable individuals (especially elderly
  targets) are the most common attack patterns.
- Traditional caller-ID and phone-based trust cues offer no protection once
  the voice itself sounds convincing.

## 3. Existing Problems / Gaps

- Deepfake-audio detection research exists, but is largely confined to
  research benchmarks, not deployed as accessible, real-time consumer or
  enterprise tools.
- Most people have no independent way to verify a caller's identity beyond
  "does this sound like them" — exactly the assumption voice cloning
  breaks.
- Existing anti-fraud tooling focuses on call metadata (number spoofing)
  rather than the audio content itself.

## 4. Our Solution

**VoiceShield AI** — a web application that:
- Analyzes uploaded or live-recorded audio for AI-generation indicators.
- Verifies the speaker against a voluntarily pre-registered trusted-speaker
  voiceprint.
- Combines both into a single, explainable risk score with a concrete,
  actionable recommendation (e.g., "verify through another channel before
  authorizing this request").
- Logs a full history and analytics dashboard so patterns of attempted
  impersonation can be reviewed over time.

## 5. System Architecture

```
Browser (React dashboard, mic capture)
        │  REST / multipart upload
        ▼
FastAPI backend
  ├─ Audio preprocessing (librosa: resample, trim, feature extraction)
  ├─ Authenticity detector (prototype classifier on acoustic features)
  ├─ Speaker verification (voiceprint embedding + cosine similarity)
  ├─ Risk engine (configurable weighted scoring + explainability)
  └─ SQLite persistence (analyses, trusted speakers, detection events)
```

## 6. AI/ML Approach

- **Feature extraction:** MFCC, mel-spectrogram, spectral centroid/
  bandwidth, zero-crossing rate, chroma, pitch (mean/variability) — a
  standard, well-understood acoustic feature set.
- **Authenticity detection:** a RandomForest classifier trained on these
  features to distinguish genuine vs. synthetic speech samples, with a
  documented, honest scope: prototype-grade, trained on a small sample set,
  not a state-of-the-art deepfake detector.
- **Speaker verification:** an MFCC-statistics voiceprint compared via
  cosine similarity — a lightweight, explainable, working alternative to a
  full neural speaker-embedding model.
- **Risk engine:** transparent, configurable weighted combination of
  authenticity anomaly, speaker mismatch, and audio-quality confidence,
  producing both a score and a human-readable explanation.
- **Demo Mode:** deterministic, clearly labeled simulated scoring so the
  system is always demonstrable regardless of environment/model
  availability.

## 7. Technology Stack

| Layer | Tech |
|---|---|
| Frontend | React, Vite, Tailwind CSS, Recharts, Web Audio API |
| Backend | Python, FastAPI, Uvicorn |
| AI/ML | librosa, numpy, scipy, scikit-learn |
| Database | SQLite + SQLAlchemy |

All components run on a standard laptop CPU — no GPU or cloud
infrastructure required.

## 8. Innovation

- Combines **two independent signals** (authenticity + speaker identity)
  into one actionable risk score, rather than a single opaque "real/fake"
  label.
- Explainability-first design: every score is backed by a visible list of
  detected signals, not a black box.
- Built-in Demo Mode makes the system reliably demonstrable — a practical
  engineering choice for hackathon and pilot contexts where model/data
  availability can be inconsistent.
- Privacy-conscious by design: only derived voiceprint embeddings are
  stored for trusted speakers, never raw reference recordings.

## 9. Features

- Upload or live-record audio for analysis.
- AI-generated probability, speaker match %, and overall risk score.
- Explainable detected-signals list per analysis.
- Trusted speaker registration and management.
- Full detection history with search/delete.
- Threat analytics dashboard (risk distribution, timelines, correlations).
- Actionable, plain-language security recommendations on high risk.

## 10. Security

- Uploaded file validation (type, size), filename sanitization, storage
  outside executable paths.
- Only voiceprint embeddings persisted for trusted speakers — raw
  reference audio is deleted immediately after processing.
- Centralized error handling — no stack traces exposed to clients.
- Configurable CORS restricted to the frontend origin.
- Explicitly scoped as MVP-level security, not independently audited or
  production-hardened.

## 11. Scalability

- Stateless FastAPI backend can be containerized and horizontally scaled
  behind a load balancer.
- SQLite is an MVP choice; a production deployment would migrate to
  PostgreSQL with the same SQLAlchemy models.
- The prototype classifier can be replaced with a pretrained
  deepfake-detection model and the MFCC voiceprint with a neural
  speaker-embedding model (e.g., ECAPA-TDNN) without changing the API
  contract — both are already abstracted behind swappable service modules.

## 12. Future Scope

- Integrate a pretrained, benchmarked deepfake-audio detection model
  (network/compute permitting).
- Upgrade speaker verification to a neural embedding model trained on
  large multi-speaker corpora.
- True streaming/continuous inference for call-center and live-call
  use cases, instead of chunked near-real-time analysis.
- Mobile app / telephony integration for real-world call screening.
- Multi-language and accent-robustness testing.
- Formal red-team evaluation against a range of voice-cloning tools.

## 13. Expected Impact

A practical, explainable first line of defense against a fast-growing
fraud vector — giving individuals, call centers, and organizations a way
to flag suspicious voice interactions and prompt independent verification
before high-stakes actions (money transfers, OTP sharing, confidential
disclosures) are taken.

## 14. Demo Flow (for judges)

1. Dashboard overview.
2. Analyze a genuine sample → LOW risk.
3. Analyze a synthetic/cloned sample → HIGH risk, with signals shown.
4. Register a trusted speaker.
5. Analyze a mismatched voice claiming that identity → speaker mismatch
   flagged, risk elevated.
6. Review detection history and threat analytics.

---

*All claims in this document are scoped to an MVP/prototype
demonstration. No accuracy figures should be quoted beyond what your own
`scripts/train_classifier.py` evaluation run actually reports on your
sample set.*
