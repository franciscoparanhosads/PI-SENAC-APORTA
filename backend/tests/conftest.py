"""
Configuração compartilhada dos testes automatizados.

- Os testes usam um banco SQLite TEMPORÁRIO, criado do zero a cada teste —
  o aporta.db de verdade nunca é tocado.
- A brapi.dev nunca é chamada de verdade: a chamada HTTP é substituída por uma
  resposta falsa, para os testes funcionarem sem internet e sempre darem o
  mesmo resultado.
"""
import os
import tempfile
from datetime import date

# As variáveis precisam existir ANTES de importar o back-end, porque database.py
# e auth.py leem o ambiente no momento do import (o load_dotenv não sobrescreve
# variáveis que já existem, então o .env real é ignorado aqui).
_TEST_DB_PATH = os.path.join(tempfile.gettempdir(), "aporta_testes.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"
os.environ["JWT_SECRET_KEY"] = "chave-usada-apenas-nos-testes"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import quotes_service  # noqa: E402
from auth import hash_password  # noqa: E402
from database import Base, SessionLocal, engine  # noqa: E402
from main import app  # noqa: E402
from models import Asset, User  # noqa: E402

SENHA_PADRAO = "senha123"


@pytest.fixture(autouse=True)
def banco_limpo():
    """Recria todas as tabelas antes de cada teste (cada teste começa do zero)."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(autouse=True)
def sem_internet(monkeypatch):
    """Garante que nenhum teste chame a brapi.dev de verdade e limpa o cache
    de cotações entre um teste e outro."""
    quotes_service._cache.clear()
    quotes_service._failed_until.clear()

    def chamada_bloqueada(*args, **kwargs):
        raise AssertionError("Teste tentou acessar a internet (brapi.dev).")

    monkeypatch.setattr(quotes_service.httpx, "get", chamada_bloqueada)
    yield
    quotes_service._cache.clear()
    quotes_service._failed_until.clear()


@pytest.fixture
def client():
    return TestClient(app)


def criar_usuario(email: str, nome: str = "Usuária Teste") -> User:
    db = SessionLocal()
    try:
        user = User(
            name=nome,
            email=email,
            password_hash=hash_password(SENHA_PADRAO),
            persona="iniciante",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def criar_ativo(user_id: int, **campos) -> Asset:
    dados = dict(
        asset_class="fii",
        code="HGLG11",
        name="CSHG Logística FII",
        quantity=10,
        amount_invested=1600.0,
        purchase_date=date(2025, 1, 10),
    )
    dados.update(campos)
    db = SessionLocal()
    try:
        asset = Asset(user_id=user_id, **dados)
        db.add(asset)
        db.commit()
        db.refresh(asset)
        return asset
    finally:
        db.close()


def fazer_login(client: TestClient, email: str) -> dict:
    """Faz login e devolve o header Authorization pronto para usar."""
    resposta = client.post("/login", json={"email": email, "password": SENHA_PADRAO})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


@pytest.fixture
def ana(client):
    """Usuária logada, já com o header de autenticação."""
    user = criar_usuario("ana@teste.com", "Ana Lima")
    return {"user": user, "headers": fazer_login(client, "ana@teste.com")}


@pytest.fixture
def bruno(client):
    """Um segundo usuário, para testar que um não acessa os dados do outro."""
    user = criar_usuario("bruno@teste.com", "Bruno Reis")
    return {"user": user, "headers": fazer_login(client, "bruno@teste.com")}
