import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    version="0.1.0",
)

# CORS: só a origem do front-end configurada no .env pode chamar esta API.
# allow_credentials=False porque a autenticação vai no header Authorization
# (Bearer), não em cookies — então não há credenciais de navegador a liberar.
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5500")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
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
