@echo off
REM ============================================================
REM  Aporta - inicia back-end e front-end juntos, cada um em sua
REM  propria janela, e abre o navegador.
REM
REM  Antes de usar este arquivo pela 1a vez, rode:
REM    backend\instalar.bat
REM ============================================================
cd /d "%~dp0"

if not exist "backend\venv" (
    echo.
    echo Ambiente virtual do back-end nao encontrado.
    echo Execute primeiro: backend\instalar.bat
    echo.
    pause
    exit /b 1
)

echo Iniciando o back-end (API) em uma nova janela...
start "Aporta - Backend (API)" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate.bat && uvicorn main:app --reload"

echo Aguardando a API subir...
timeout /t 3 /nobreak >nul

echo Iniciando o front-end em uma nova janela...
start "Aporta - Frontend" cmd /k "cd /d "%~dp0frontend" && python -m http.server 5500"

timeout /t 2 /nobreak >nul

echo Abrindo o navegador...
start http://localhost:5500/index.html

echo.
echo ============================================================
echo  Pronto! Duas janelas foram abertas (backend e frontend).
echo  Feche as duas janelas quando terminar de usar o sistema.
echo ============================================================
pause
