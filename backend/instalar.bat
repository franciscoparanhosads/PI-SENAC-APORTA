@echo off
REM ============================================================
REM  Aporta - instalacao do back-end (rodar apenas 1 vez).
REM  Cria o ambiente virtual, instala as dependencias, gera o
REM  arquivo .env e popula o banco com as 3 personas.
REM ============================================================
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo Python nao encontrado. Instale o Python 3.11 ou superior em
    echo https://www.python.org/downloads/ e marque "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

if not exist "venv" (
    echo Criando o ambiente virtual...
    python -m venv venv
    if errorlevel 1 goto erro
)

echo Instalando as dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 goto erro

if not exist ".env" (
    echo Criando o arquivo .env a partir do .env.example...
    copy .env.example .env >nul
)

echo Populando o banco de dados...
python seed.py
if errorlevel 1 goto erro

echo.
echo ============================================================
echo  Instalacao concluida! Agora rode o iniciar-tudo.bat
echo  (na pasta acima) para abrir o sistema.
echo ============================================================
pause
exit /b 0

:erro
echo.
echo Ocorreu um erro durante a instalacao. Veja a mensagem acima.
pause
exit /b 1
