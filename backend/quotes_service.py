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


def _get_cached(code: str) -> dict | None:
    entry = _cache.get(code)
    if entry and (time.time() - entry["fetched_at"]) < _CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def _set_cache(code: str, data: dict) -> None:
    _cache[code] = {"data": data, "fetched_at": time.time()}


def fetch_real_quote(code: str) -> dict:
    """Consulta a brapi.dev para um dos 4 tickers gratuitos, com cache e fallback."""
    cached = _get_cached(code)
    if cached is not None:
        return cached

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
        return data
    except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError):
        # brapi.dev fora do ar, resposta inesperada, etc. — nunca deixamos a
        # tela quebrar: devolvemos o último valor válido em cache (mesmo
        # vencido) ou o valor de fallback fixo. Em ambos os casos o preço NÃO
        # é atual, então is_real_time vai como False (a tela mostra "simulado").
        stale = _cache.get(code)
        if stale is not None:
            return {**stale["data"], "is_real_time": False}
        return {
            "code": code,
            "price": FALLBACK_PRICES.get(code, 0.0),
            "change_percent": 0.0,
            "is_real_time": False,
        }


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
