from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Asset, User
from quotes_service import get_quote
from schemas import QuoteOut

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.get("", response_model=list[QuoteOut])
def get_quotes_for_my_assets(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Retorna a cotação atual de cada CÓDIGO que o usuário logado possui — real
    para PETR4/MGLU3/VALE3/ITUB4, simulada para os demais.

    É uma cotação por código (não por ativo): se o usuário tem dois lotes do
    mesmo ticker, os dois são avaliados pelo mesmo preço."""
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()

    # Soma de quantidade e valor investido por código, para calcular o preço
    # médio ponderado de todos os lotes do mesmo código.
    totais: dict[str, list[float]] = {}
    for asset in assets:
        acumulado = totais.setdefault(asset.code.upper(), [0.0, 0.0])
        acumulado[0] += asset.quantity
        acumulado[1] += asset.amount_invested

    quotes = []
    for code, (quantity, invested) in totais.items():
        # Valor-base usado apenas quando a cotação é simulada: o preço médio
        # pago pelo usuário, para o mock ficar plausível.
        base_price = invested / quantity if quantity else 0.0
        quote = get_quote(code, base_price)
        quotes.append(
            QuoteOut(
                code=quote["code"],
                price=quote["price"],
                change_percent=quote["change_percent"],
                is_real_time=quote["is_real_time"],
                updated_at=datetime.now(timezone.utc),
            )
        )
    return quotes
