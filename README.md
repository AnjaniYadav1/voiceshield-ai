# 🛡️ VoiceShield AI

<p align="center">
  <img src="https://img.shields.io/badge/AI-Voice%20Security-7C3AED?style=for-the-badge" alt="AI Voice Security"/>
  <img src="https://img.shields.io/badge/Deepfake-Detection-EF4444?style=for-the-badge" alt="Deepfake Detection"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Status-MVP-22C55E?style=for-the-badge" alt="MVP"/>
</p>

<h3 align="center">
  🎙️ Detect. Verify. Prevent Voice Impersonation.
</h3>

<p align="center">
  <b>VoiceShield AI</b> is an AI-powered defensive voice security system that analyzes audio,
  detects potential AI-generated or cloned voices, verifies speaker identity,
  and provides an explainable impersonation risk assessment.
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-roadmap">Roadmap</a>
</p>

---

## 🚨 The Problem

With the rapid growth of Generative AI, voice cloning technology has become increasingly realistic.

Attackers can potentially use cloned voices for:

- 💰 Financial fraud
- 🎭 Identity impersonation
- 📞 Social engineering
- 🏦 Banking scams
- 👨‍👩‍👧 Family and emergency scams
- 🏢 Corporate impersonation
- 🔐 Voice-based authentication attacks

Traditional voice-based trust is no longer enough.

**VoiceShield AI provides an additional layer of defense by analyzing voice characteristics and verifying whether a speaker matches a trusted identity.**

---

## 💡 What is VoiceShield AI?

VoiceShield AI is an AI-powered voice security platform designed to detect potential **voice cloning, synthetic speech, and speaker impersonation**.

The system combines multiple security signals:

```text
🎙️ Audio Analysis
        +
🤖 Synthetic Voice Detection
        +
👤 Speaker Verification
        ↓
⚠️ Impersonation Risk Engine
        ↓
🟢 LOW / 🟡 MEDIUM / 🔴 HIGH
```


## ✨ Features

### 🎙️ AI Voice Detection

Analyze audio recordings for characteristics associated with **AI-generated or cloned speech**.

### 👤 Speaker Verification

Register a trusted speaker and compare future recordings against their **voice profile**.

### ⚠️ Risk Assessment

Multiple signals are combined into an easy-to-understand **risk level**.

| Risk Level | Meaning |
|------------|---------|
| 🟢 **LOW** | No significant impersonation indicators detected |
| 🟡 **MEDIUM** | Suspicious indicators detected |
| 🔴 **HIGH** | Strong impersonation indicators detected |

```
```

## 📊 Explainable Results

Instead of simply returning `REAL` or `FAKE`, VoiceShield provides:

- AI voice detection score
- Speaker similarity
- Detected signals
- Overall risk level
- Recommended action

## 🎤 Live Audio Analysis

Analyze audio directly through the browser microphone.

## 📁 Audio Upload

Upload supported audio recordings for analysis.

## 👤 Speaker Registration

Create trusted speaker profiles for future identity verification.

## 📜 Detection History

View previously analyzed recordings and their results.

## 📈 Threat Analytics

Track analysis activity and visualize threat statistics through the dashboard.

## 🧪 Demo & Real ML Modes

The system supports:

- **Demo Mode** — deterministic results for reliable demonstrations
- **Real ML Mode** — prototype feature-based audio analysis
- **Auto Mode** — automatically uses the available analysis pipeline

> ⚠️ Demo results are clearly labeled and should not be interpreted as real-world detection predictions.

# 🧠 How It Works

```text
                ┌────────────────────┐
                │   Audio Recording  │
                └─────────┬──────────┘
                          │
                          ▼
                ┌────────────────────┐
                │ Audio Preprocessing│
                └─────────┬──────────┘
                          │
                          ▼
             ┌──────────────────────────┐
             │   Acoustic Feature       │
             │       Extraction         │
             │                          │
             │ • MFCC                   │
             │ • Mel Spectrogram        │
             │ • Spectral Features      │
             │ • Chroma                 │
             │ • Pitch Statistics       │
             │ • Zero Crossing Rate     │
             └────────────┬─────────────┘
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
       ┌────────────────┐   ┌─────────────────┐
       │ Voice Detection│   │ Speaker         │
       │                │   │ Verification    │
       └───────┬────────┘   └────────┬────────┘
               │                     │
               └──────────┬──────────┘
                          ▼
                ┌────────────────────┐
                │   Risk Assessment  │
                │      Engine        │
                └─────────┬──────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │ LOW / MEDIUM / HIGH │
               └─────────────────────┘
```

### 🔍 Detection Pipeline

1. 🎙️ User uploads or records audio.
2. 🔒 VoiceShield validates and preprocesses the audio.
3. 🎵 Acoustic features are extracted.
4. 🤖 The system analyzes characteristics associated with synthetic speech.
5. 👤 The speaker can be compared with a registered voice profile.
6. ⚠️ Detection signals are passed to the risk engine.
7. 📊 The system generates an impersonation-risk assessment.
8. 🖥️ Results are displayed through the dashboard.

# 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │     React Frontend   │
                    │   Dashboard + UI     │
                    └──────────┬───────────┘
                               │
                               │ HTTP / REST
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI Backend  │
                    │                      │
                    │  /analyze            │
                    │  /analyze/live       │
                    │  /speakers/register  │
                    │  /statistics         │
                    └──────────┬───────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐           ┌─────────────────┐
       │ Audio Processing│           │ Speaker         │
       │                 │           │ Verification    │
       │ MFCC            │           │                 │
       │ Mel Spectrogram │           │ Voice Embedding │
       │ Pitch           │           │ Similarity      │
       │ Spectral Stats  │           └────────┬────────┘
       └────────┬────────┘                    │
                │                             │
                └──────────────┬──────────────┘
                               ▼
                    ┌──────────────────────┐
                    │     Risk Engine      │
                    │                      │
                    │ LOW / MEDIUM / HIGH  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ SQLite / Analytics   │
                    │ History + Statistics │
                    └──────────────────────┘
```
# 🛠️ Tech Stack

VoiceShield AI is built using modern web, backend, audio-processing, and machine-learning technologies.

| Layer | Technology | Purpose |
|---|---|---|
| 🎨 Frontend | **React.js** | Interactive user interface |
| ⚡ Build Tool | **Vite** | Fast frontend development and builds |
| 🎨 Styling | **Tailwind CSS** | Responsive and modern UI |
| 🐍 Backend | **Python** | Backend and ML processing |
| 🚀 API | **FastAPI** | High-performance REST API |
| 🎵 Audio Processing | **Librosa** | Audio analysis and feature extraction |
| 🧠 Machine Learning | **Scikit-learn** | Prototype voice classification |
| 🎙️ Voice Features | **MFCC, Chroma, Pitch, Spectral Features** | Voice and audio analysis |
| 👤 Speaker Verification | **MFCC-based Voice Embeddings** | Speaker similarity comparison |
| 🗄️ Database | **SQLite** | Analysis history and speaker data |
| 🌐 Communication | **REST API** | Frontend-backend communication |
| 🔧 Version Control | **Git & GitHub** | Source code management |


### 🧠 AI / Audio Processing

The current prototype analyzes several acoustic characteristics:

- **MFCC** — Mel-Frequency Cepstral Coefficients
- **Mel-Spectrogram** features
- **Spectral Centroid**
- **Spectral Bandwidth**
- **Zero-Crossing Rate**
- **Chroma Features**
- **Pitch Statistics**

These features are used for prototype synthetic-voice analysis and speaker verification.

> **Note:** The current repository is an MVP/prototype and does not bundle a production-grade pretrained deepfake detector or neural speaker-embedding model.

# 📂 Project Structure

```text
voiceshield-ai/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   ├── genuine/
│   └── synthetic/
│
├── models/
│
├── docs/
│
├── .env.example
├── run.bat
├── run.py
├── package.json
└── README.md

```
# 🚀 Installation

Follow the steps below to run VoiceShield AI locally.

## 📋 Prerequisites

Make sure the following are installed:

- 🐍 **Python 3.10 or higher**
- 🟢 **Node.js 18 or higher**
- 📦 **npm**
- 🔧 **Git**


### 1️⃣ Clone the Repository
```
git clone https://github.com/AnjaniYadav1/voiceshield-ai.git
cd voiceshield-ai

```
## 2️⃣ Backend Setup

Navigate to the backend:
```
cd backend
```
Create a Python virtual environment:

Windows
```
python -m venv venv
venv\Scripts\activate
```
Linux / macOS
```
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:
```
pip install -r requirements.txt
```
## 3️⃣ Environment Configuration

Create your environment file from the example configuration.

### Windows

```bash
copy ..\.env.example .env
```
Linux / macOS
```
cp ../.env.example .env
```
Update the .env file according to your local configuration.

## 4️⃣ Start the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload --port 8000
```
The FastAPI backend will be available at:
```
http://127.0.0.1:8000
```
📚 API Documentation

FastAPI automatically provides interactive API documentation:
```
http://127.0.0.1:8000/docs
```
## 5️⃣ Frontend Setup

Open a new terminal and navigate to the frontend:

```bash
cd frontend
```
Install frontend dependencies:
```
npm install
```
Start the development server:
```
npm run dev
```
The frontend will normally be available at:
```
http://localhost:5173
```
# ⚡ Quick Start — Windows

For a quick setup, the project includes a startup script.

From the project root:

```bat
run.bat
```
Then open:
```
http://127.0.0.1:8000
```
The application can then be accessed through a single URL.

# 🧪 Demo Mode

VoiceShield AI includes a deterministic **Demo Mode** for reliable demonstrations.

Demo Mode allows the complete application workflow to be demonstrated even when the ML pipeline is unavailable.

The interface clearly labels simulated results.

> ⚠️ Demo results are simulated and must not be interpreted as real-world detection predictions.

For production environments, security decisions should never silently fall back to simulated results.

# 🤖 Real ML Mode

The project also supports a prototype ML pipeline using audio datasets.

Place genuine samples in:

```text
data/genuine/
```
Place synthetic or cloned samples in:
```
data/synthetic/
```
Follow the training instructions available in:
```
backend/README.md
```
Model artifacts can be stored in:
```
models/
```
