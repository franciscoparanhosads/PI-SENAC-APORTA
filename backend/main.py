import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from routers import assets_routes, auth_routes, quotes_routes, simulator_routes

load_dotenv()

# Cria as tabelas no SQLite se ainda não existirem (não apaga dados existentes).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aporta — API do protótipo",
    description=(
        "API do protótipo acadêmico de gestão e análise de investimentos "
        "pessoais. Este serviço apenas informa e simula dados — nunca "
        "recomenda a compra ou venda de ativos."
    ),
    version="0.2.0",
)

# CORS: só a origem do front-end configurada no .env pode chamar esta API.
# allow_credentials=False porque a autenticação vai no header Authorization
# (Bearer), não em cookies — então não há credenciais de navegador a liberar.
# FRONTEND_ORIGIN aceita várias origens separadas por vírgula; por padrão libera
# tanto "localhost" quanto "127.0.0.1" (o navegador trata os dois como origens
# diferentes).
DEFAULT_ORIGINS = "http://localhost:5500,http://127.0.0.1:5500"
frontend_origins = [
    origem.strip().rstrip("/")
    for origem in os.getenv("FRONTEND_ORIGIN", DEFAULT_ORIGINS).split(",")
    if origem.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_routes.router)
app.include_router(assets_routes.router)
app.include_router(quotes_routes.router)
app.include_router(simulator_routes.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


# Serve o front-end pelo próprio back-end (http://localhost:8000).
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
