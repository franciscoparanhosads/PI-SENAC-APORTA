@echo off
REM ============================================================
REM  Aporta - roda os testes automatizados do back-end.
REM  Usa um banco temporario: o aporta.db NAO e alterado.
REM ============================================================
cd /d "%~dp0"

if not exist "venv" (
    echo.
    echo Ambiente virtual nao encontrado. Execute primeiro: instalar.bat
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

python -c "import pytest" 2>nul
if errorlevel 1 (
    echo Instalando o pytest...
    pip install -r requirements.txt
)

python -m pytest
echo.
pause
