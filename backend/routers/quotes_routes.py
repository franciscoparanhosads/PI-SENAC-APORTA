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
    """Retorna a cotação atual de cada ativo do usuário logado — real para
    PETR4/MGLU3/VALE3/ITUB4, simulada para os demais."""
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()

    quotes = []
    for asset in assets:
        # Valor-base usado apenas quando a cotação é simulada: o próprio
        # preço médio pago pelo usuário, para o mock ficar plausível.
        base_price = asset.amount_invested / asset.quantity if asset.quantity else 0.0
        quote = get_quote(asset.code, base_price)
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
