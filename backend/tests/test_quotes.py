"""Testes das cotações: brapi.dev (simulada nos testes), cache, fallback e mock."""
import httpx
import pytest

import quotes_service

from conftest import criar_ativo


class RespostaFalsaBrapi:
    """Imita a resposta da brapi.dev, sem acessar a internet."""

    def __init__(self, preco, variacao=1.25):
        self._preco = preco
        self._variacao = variacao

    def raise_for_status(self):
        pass

    def json(self):
        return {"results": [{"regularMarketPrice": self._preco, "regularMarketChangePercent": self._variacao}]}


@pytest.fixture
def brapi_no_ar(monkeypatch):
    """brapi.dev respondendo normalmente; guarda quantas vezes foi chamada."""
    chamadas = []

    def get_falso(url, **kwargs):
        chamadas.append(url)
        return RespostaFalsaBrapi(preco=40.0)

    monkeypatch.setattr(quotes_service.httpx, "get", get_falso)
    return chamadas


@pytest.fixture
def brapi_fora_do_ar(monkeypatch):
    def get_falso(url, **kwargs):
        raise httpx.ConnectError("brapi.dev fora do ar")

    monkeypatch.setattr(quotes_service.httpx, "get", get_falso)


# ---------- serviço de cotações ----------

def test_ticker_gratuito_usa_cotacao_real(brapi_no_ar):
    cotacao = quotes_service.get_quote("petr4", base_price_if_mock=0)

    assert cotacao == {"code": "PETR4", "price": 40.0, "change_percent": 1.25, "is_real_time": True}
    assert brapi_no_ar == [f"{quotes_service.BRAPI_BASE_URL}/PETR4"]


def test_cache_evita_chamar_a_brapi_de_novo(brapi_no_ar):
    quotes_service.get_quote("VALE3", 0)
    quotes_service.get_quote("VALE3", 0)
    quotes_service.get_quote("VALE3", 0)

    assert len(brapi_no_ar) == 1  # só a primeira consulta foi à internet


def test_brapi_fora_do_ar_sem_cache_usa_valor_fixo_marcado_como_simulado(brapi_fora_do_ar):
    cotacao = quotes_service.get_quote("PETR4", 0)

    assert cotacao["price"] == quotes_service.FALLBACK_PRICES["PETR4"]
    assert cotacao["is_real_time"] is False


def test_brapi_fora_do_ar_com_cache_vencido_usa_ultimo_valor_conhecido(brapi_fora_do_ar):
    quotes_service._cache["ITUB4"] = {
        "data": {"code": "ITUB4", "price": 35.0, "change_percent": 0.5, "is_real_time": True},
        "fetched_at": 0,  # cache muito antigo, já vencido
    }

    cotacao = quotes_service.get_quote("ITUB4", 0)

    assert cotacao["price"] == 35.0
    assert cotacao["is_real_time"] is False  # o preço não é atual


def test_outros_codigos_recebem_cotacao_simulada_perto_do_preco_base():
    for _ in range(50):  # a variação é aleatória: testamos várias vezes
        cotacao = quotes_service.get_quote("HGLG11", base_price_if_mock=100.0)

        assert cotacao["is_real_time"] is False
        assert 98.5 <= cotacao["price"] <= 101.5  # no máximo ±1,5%
        assert -1.5 <= cotacao["change_percent"] <= 1.5


# ---------- rota /quotes ----------

def test_rota_devolve_uma_cotacao_por_ativo_do_usuario(client, ana, bruno, brapi_no_ar):
    criar_ativo(ana["user"].id, asset_class="acao", code="PETR4", quantity=10, amount_invested=380)
    criar_ativo(ana["user"].id, code="HGLG11", quantity=10, amount_invested=1600)
    criar_ativo(bruno["user"].id, code="DO-BRUNO")

    cotacoes = client.get("/quotes", headers=ana["headers"]).json()
    por_codigo = {c["code"]: c for c in cotacoes}

    assert set(por_codigo) == {"PETR4", "HGLG11"}  # nada do Bruno
    assert por_codigo["PETR4"]["is_real_time"] is True
    assert por_codigo["PETR4"]["price"] == 40.0
    assert por_codigo["HGLG11"]["is_real_time"] is False
    # simulado em torno do preço médio pago: 1600 / 10 = 160
    assert 157.6 <= por_codigo["HGLG11"]["price"] <= 162.4
