"""
Serviço de cotações — chamado apenas pelo back-end (o front-end nunca fala
diretamente com a brapi.dev).

- Tickers em tempo real (sem necessidade de token, conforme a documentação
  pública da brapi.dev): PETR4, MGLU3, VALE3, ITUB4.
- Qualquer outro código (renda fixa, FIIs, outras ações, cripto) recebe uma
  cotação simulada (mock), com pequena variação aleatória sobre um valor-base.
- Cache simples em memória de 60s para não estourar limite de chamadas nem
  deixar a tela lenta, e um valor de fallback caso a API externa esteja fora
  do ar.
"""
import os
import random
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

BRAPI_BASE_URL = "https://brapi.dev/api/quote"
BRAPI_TOKEN = os.getenv("BRAPI_TOKEN", "").strip()

REAL_TIME_TICKERS = {"PETR4", "MGLU3", "VALE3", "ITUB4"}

# Valor de fallback usado se a brapi.dev estiver fora do ar e ainda não
# tivermos nenhum valor em cache para o ticker.
FALLBACK_PRICES = {
    "PETR4": 38.50,
    "MGLU3": 9.20,
    "VALE3": 61.30,
    "ITUB4": 33.10,
}

_cache: dict[str, dict] = {}
_CACHE_TTL_SECONDS = 60

# Quando a brapi.dev falha, guardamos até quando NÃO devemos tentar de novo.
# Sem isso, cada requisição esperaria o timeout (5s) de cada ticker enquanto a
# API estiver fora do ar.
_failed_until: dict[str, float] = {}
_FAILURE_BACKOFF_SECONDS = 60


def _get_cached(code: str) -> dict | None:
    entry = _cache.get(code)
    if entry and (time.time() - entry["fetched_at"]) < _CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def _set_cache(code: str, data: dict) -> None:
    _cache[code] = {"data": data, "fetched_at": time.time()}


def _fallback_quote(code: str) -> dict:
    """Último valor válido em cache (mesmo vencido) ou o valor fixo. Em ambos os
    casos o preço NÃO é atual, então is_real_time vai como False."""
    stale = _cache.get(code)
    if stale is not None:
        return {**stale["data"], "is_real_time": False}
    return {
        "code": code,
        "price": FALLBACK_PRICES.get(code, 0.0),
        "change_percent": 0.0,
        "is_real_time": False,
    }


def fetch_real_quote(code: str) -> dict:
    """Consulta a brapi.dev para um dos 4 tickers gratuitos, com cache e fallback."""
    cached = _get_cached(code)
    if cached is not None:
        return cached

    # A brapi falhou há pouco: não tenta de novo agora, usa o fallback direto.
    if time.time() < _failed_until.get(code, 0.0):
        return _fallback_quote(code)

    params = {}
    if BRAPI_TOKEN:
        params["token"] = BRAPI_TOKEN

    try:
        response = httpx.get(f"{BRAPI_BASE_URL}/{code}", params=params, timeout=5.0)
        response.raise_for_status()
        payload = response.json()
        result = payload["results"][0]
        data = {
            "code": code,
            "price": float(result["regularMarketPrice"]),
            "change_percent": float(result.get("regularMarketChangePercent", 0.0)),
            "is_real_time": True,
        }
        _set_cache(code, data)
        _failed_until.pop(code, None)
        return data
    except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError):
        # brapi.dev fora do ar, resposta inesperada, etc. — nunca deixamos a
        # tela quebrar, e só voltamos a tentar depois do período de espera.
        _failed_until[code] = time.time() + _FAILURE_BACKOFF_SECONDS
        return _fallback_quote(code)


def mock_quote(code: str, base_price: float) -> dict:
    """Cotação simulada: pequena variação aleatória (±1,5%) sobre um valor-base."""
    variation = random.uniform(-0.015, 0.015)
    price = round(base_price * (1 + variation), 2)
    return {
        "code": code,
        "price": price,
        "change_percent": round(variation * 100, 2),
        "is_real_time": False,
    }


def get_quote(code: str, base_price_if_mock: float) -> dict:
    code = code.upper()
    if code in REAL_TIME_TICKERS:
        return fetch_real_quote(code)
    return mock_quote(code, base_price_if_mock)
