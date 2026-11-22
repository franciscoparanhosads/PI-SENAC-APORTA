"""
Inicia o Aporta com UM comando, em qualquer sistema (Windows, macOS, Linux):

    python run.py

Cria o .env (com chave aleatória) e o banco com as 3 personas se ainda não
existirem, sobe a API + o front-end em http://localhost:8000 e abre o navegador.
Requer as dependências instaladas:  pip install -r backend/requirements.txt
"""
import os
import sys
import threading
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BACKEND = RAIZ / "backend"
PORTA = 8000

os.chdir(BACKEND)               # o aporta.db e o .env ficam em backend/
sys.path.insert(0, str(BACKEND))

try:
    import uvicorn
    from dotenv import load_dotenv  # noqa: F401
except ImportError:
    sys.exit("Dependências não instaladas. Rode:  pip install -r backend/requirements.txt")

from gerar_env import gerar_env

if gerar_env():
    print("• .env criado com uma chave JWT aleatória.")

import seed  # noqa: E402  (precisa vir depois do .env existir)

seed.run_seed()  # idempotente: pula quem já existe

threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORTA}/")).start()
print(f"\nAporta rodando em http://localhost:{PORTA}/  (Ctrl+C para parar)\n")
uvicorn.run("main:app", host="127.0.0.1", port=PORTA)
