@echo off
echo.
echo  ╔══════════════════════════════════════╗
echo  ║    AI Alarm System 2026 - Setup      ║
echo  ╚══════════════════════════════════════╝
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/4] Installing dependencies...
pip install customtkinter pygame numpy pyttsx3 SpeechRecognition

echo [3/4] Trying pyaudio (for voice control)...
pip install pyaudio 2>nul || (
    pip install pipwin 2>nul
    pipwin install pyaudio 2>nul
)

echo [4/4] Launching AI Alarm System...
python main.py

pause
