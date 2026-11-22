"""
Schemas Pydantic — validam TODA entrada e saída da API.

Nenhum dado bruto do usuário chega ao banco sem passar por um desses schemas
(tipos, tamanhos, formatos de e-mail, valores de classe restritos a um conjunto
fechado de opções). Isso barra dados malformados.

Atenção: validar tipo/tamanho NÃO impede XSS — um nome como
`<script>...</script>` é um texto válido. A proteção contra XSS fica no
front-end, que escapa todo texto antes de inseri-lo no HTML (ver
`escapeHtml` em frontend/js/utils.js).
"""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

AssetClass = Literal["renda_fixa", "fii", "acao", "cripto"]


# ---------- Autenticação ----------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str
    persona: str


# ---------- Ativos ----------

class AssetCreate(BaseModel):
    asset_class: AssetClass
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=120)
    quantity: float = Field(gt=0)
    amount_invested: float = Field(gt=0)
    purchase_date: date


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_class: AssetClass
    code: str
    name: str
    quantity: float
    amount_invested: float
    purchase_date: date


# ---------- Cotações ----------

class QuoteOut(BaseModel):
    asset_id: int  # id do ativo cadastrado: dois aportes no mesmo código têm cotações distintas
    code: str
    price: float
    change_percent: float
    is_real_time: bool  # True apenas para PETR4, MGLU3, VALE3, ITUB4
    updated_at: datetime


# ---------- Simulador ----------

class SimulationRequest(BaseModel):
    current_amount: float = Field(ge=0)
    monthly_contribution: float = Field(ge=0)
    annual_return_rate: float = Field(gt=0, le=100)  # em %, ex: 9.5
    goal_amount: float = Field(gt=0)


class SimulationPoint(BaseModel):
    month: int
    amount: float


class SimulationResponse(BaseModel):
    reachable: bool
    months_to_goal: int | None
    years: int | None
    months: int | None
    projection: list[SimulationPoint]
