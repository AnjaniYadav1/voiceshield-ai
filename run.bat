@echo off
REM VoiceShield AI - single-command launcher (Windows)
REM Builds the frontend once, then starts the backend, which serves both
REM the API and the frontend from the same address. Only one window/URL
REM to deal with after this.

setlocal

echo ============================================
echo  VoiceShield AI - Setup and Run
echo ============================================

REM --- Backend venv + deps ---
if not exist backend\venv (
    echo Creating Python virtual environment...
    python -m venv backend\venv
)

call backend\venv\Scripts\activate.bat

echo Installing backend dependencies (first run only, may take a few minutes)...
pip install -r backend\requirements.txt

if not exist backend\.env (
    copy .env.example backend\.env >nul
)

REM --- Frontend build ---
echo Installing frontend dependencies (first run only)...
pushd frontend
call npm install
echo Building frontend...
call npm run build
popd

REM --- Run combined app ---
echo.
echo ============================================
echo  Starting VoiceShield AI at http://127.0.0.1:8000
echo  Press CTRL+C to stop.
echo ============================================
cd backend
uvicorn app.main:app --port 8000

endlocal
