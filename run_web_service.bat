@echo off
REM Define la ruta del entorno virtual
set VENV_DIR=.\venv

REM Activa el entorno virtual
call %VENV_DIR%\Scripts\activate.bat

REM Entrar a la ruta src donde esta el código principal
cd src

REM Inicia el servicio de FastAPI
uvicorn main:app --reload --host 0.0.0.0 --port 8000

echo Entorno virtual completo.
pause
