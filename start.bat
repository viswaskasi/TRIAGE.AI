@echo off
title Support Triage AI Agent
echo ==========================================
echo   Support Triage AI Agent - Starting...
echo ==========================================
echo.
echo  Backend : FastAPI + Gemini + RAG (ChromaDB)
echo  Frontend: http://127.0.0.1:8001
echo.
echo  Press CTRL+C to stop the server.
echo ==========================================
echo.
cd /d "%~dp0backend"
python -m uvicorn main:app --port 8001 --reload
pause
