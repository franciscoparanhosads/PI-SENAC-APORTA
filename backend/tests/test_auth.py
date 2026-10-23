"""Testes de autenticação: login, senha com hash e proteção das rotas por JWT."""
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from auth import JWT_ALGORITHM, JWT_SECRET_KEY, create_access_token
from database import SessionLocal
from models import User

from conftest import SENHA_PADRAO, criar_usuario


def test_login_com_dados_corretos_devolve_token(client):
    criar_usuario("ana@teste.com", "Ana Lima")

    resposta = client.post("/login", json={"email": "ana@teste.com", "password": SENHA_PADRAO})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["access_token"]
    assert corpo["token_type"] == "bearer"
    assert corpo["user_name"] == "Ana Lima"
    assert corpo["persona"] == "iniciante"


def test_senha_errada_e_email_inexistente_dao_a_mesma_mensagem(client):
    """A mensagem é igual nos dois casos para não revelar quais e-mails estão
    cadastrados (proteção contra enumeração de usuários)."""
    criar_usuario("ana@teste.com")

    senha_errada = client.post("/login", json={"email": "ana@teste.com", "password": "errada123"})
    email_inexistente = client.post("/login", json={"email": "ninguem@teste.com", "password": "qualquer123"})

    assert senha_errada.status_code == 401
    assert email_inexistente.status_code == 401
    assert senha_errada.json()["detail"] == email_inexistente.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "nao-e-um-email", "password": "senha123"},
        {"email": "ana@teste.com", "password": "123"},  # menos de 6 caracteres
        {"email": "ana@teste.com"},  # sem senha
    ],
)
def test_login_com_dados_malformados_e_rejeitado(client, payload):
    resposta = client.post("/login", json=payload)
    assert resposta.status_code == 422


def test_senha_nunca_e_salva_em_texto_puro():
    criar_usuario("ana@teste.com")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "ana@teste.com").one()
    finally:
        db.close()

    assert user.password_hash != SENHA_PADRAO
    assert user.password_hash.startswith("$2b$")  # formato do hash bcrypt


@pytest.mark.parametrize("rota", ["/assets", "/quotes"])
def test_rota_protegida_sem_token_e_bloqueada(client, rota):
    assert client.get(rota).status_code == 401


def test_simulador_sem_token_e_bloqueado(client):
    payload = {"current_amount": 0, "monthly_contribution": 100, "annual_return_rate": 10, "goal_amount": 1000}
    assert client.post("/simulate", json=payload).status_code == 401


def test_token_invalido_e_bloqueado(client):
    resposta = client.get("/assets", headers={"Authorization": "Bearer token-inventado"})
    assert resposta.status_code == 401


def test_token_assinado_com_outra_chave_e_bloqueado(client):
    user = criar_usuario("ana@teste.com")
    token_falso = jwt.encode({"sub": str(user.id)}, "chave-de-um-atacante", algorithm=JWT_ALGORITHM)

    resposta = client.get("/assets", headers={"Authorization": f"Bearer {token_falso}"})
    assert resposta.status_code == 401


def test_token_expirado_e_bloqueado(client):
    user = criar_usuario("ana@teste.com")
    expirou_ha_1_minuto = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": str(user.id), "exp": expirou_ha_1_minuto}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
    )

    resposta = client.get("/assets", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401


def test_token_de_usuario_que_nao_existe_mais_e_bloqueado(client):
    token = create_access_token(user_id=9999)

    resposta = client.get("/assets", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401
