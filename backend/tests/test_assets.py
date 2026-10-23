"""Testes do cadastro de ativos: criar, listar, validar e remover."""
from datetime import date

import pytest

from conftest import criar_ativo

ATIVO_VALIDO = {
    "asset_class": "acao",
    "code": "  petr4 ",
    "name": "  Petrobras PN ",
    "quantity": 10,
    "amount_invested": 380.0,
    "purchase_date": "2025-03-15",
}


def test_lista_comeca_vazia(client, ana):
    resposta = client.get("/assets", headers=ana["headers"])
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_criar_ativo_padroniza_codigo_e_nome(client, ana):
    resposta = client.post("/assets", json=ATIVO_VALIDO, headers=ana["headers"])

    assert resposta.status_code == 201
    ativo = resposta.json()
    assert ativo["code"] == "PETR4"  # maiúsculo e sem espaços
    assert ativo["name"] == "Petrobras PN"  # sem espaços nas pontas
    assert ativo["quantity"] == 10
    assert ativo["purchase_date"] == "2025-03-15"


def test_ativo_criado_aparece_na_lista(client, ana):
    client.post("/assets", json=ATIVO_VALIDO, headers=ana["headers"])

    lista = client.get("/assets", headers=ana["headers"]).json()
    assert [a["code"] for a in lista] == ["PETR4"]


def test_lista_vem_do_aporte_mais_recente_para_o_mais_antigo(client, ana):
    user_id = ana["user"].id
    criar_ativo(user_id, code="ANTIGO", purchase_date=date(2023, 1, 1))
    criar_ativo(user_id, code="RECENTE", purchase_date=date(2025, 6, 1))
    criar_ativo(user_id, code="MEIO", purchase_date=date(2024, 6, 1))

    lista = client.get("/assets", headers=ana["headers"]).json()
    assert [a["code"] for a in lista] == ["RECENTE", "MEIO", "ANTIGO"]


@pytest.mark.parametrize(
    "campo, valor_invalido",
    [
        ("asset_class", "poupanca"),  # classe fora das 4 permitidas
        ("quantity", 0),
        ("quantity", -5),
        ("amount_invested", 0),
        ("amount_invested", -100),
        ("code", ""),
        ("code", "X" * 31),  # passa do limite de 30 caracteres
        ("name", ""),
        ("purchase_date", "31/12/2025"),  # formato de data errado
    ],
)
def test_ativo_com_dado_invalido_e_rejeitado(client, ana, campo, valor_invalido):
    payload = {**ATIVO_VALIDO, campo: valor_invalido}

    resposta = client.post("/assets", json=payload, headers=ana["headers"])

    assert resposta.status_code == 422
    # e nada foi salvo
    assert client.get("/assets", headers=ana["headers"]).json() == []


def test_usuario_so_ve_os_proprios_ativos(client, ana, bruno):
    criar_ativo(ana["user"].id, code="DA-ANA")
    criar_ativo(bruno["user"].id, code="DO-BRUNO")

    lista_ana = client.get("/assets", headers=ana["headers"]).json()
    lista_bruno = client.get("/assets", headers=bruno["headers"]).json()

    assert [a["code"] for a in lista_ana] == ["DA-ANA"]
    assert [a["code"] for a in lista_bruno] == ["DO-BRUNO"]


def test_remover_ativo_proprio(client, ana):
    ativo = criar_ativo(ana["user"].id)

    resposta = client.delete(f"/assets/{ativo.id}", headers=ana["headers"])

    assert resposta.status_code == 204
    assert client.get("/assets", headers=ana["headers"]).json() == []


def test_remover_ativo_inexistente_da_404(client, ana):
    resposta = client.delete("/assets/9999", headers=ana["headers"])
    assert resposta.status_code == 404


def test_usuario_nao_consegue_remover_ativo_de_outra_pessoa(client, ana, bruno):
    """Mesmo sabendo o id, o Bruno não pode apagar o ativo da Ana."""
    ativo_da_ana = criar_ativo(ana["user"].id)

    resposta = client.delete(f"/assets/{ativo_da_ana.id}", headers=bruno["headers"])

    assert resposta.status_code == 404
    lista_ana = client.get("/assets", headers=ana["headers"]).json()
    assert [a["id"] for a in lista_ana] == [ativo_da_ana.id]  # continua lá
