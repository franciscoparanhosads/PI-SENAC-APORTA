import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Asset, User
from schemas import AssetCreate, AssetOut

logger = logging.getLogger("aporta")

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetOut])
def list_assets(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(Asset)
        .filter(Asset.user_id == current_user.id)
        .order_by(Asset.purchase_date.desc())
        .all()
    )


@router.post("", response_model=AssetOut, status_code=status.HTTP_201_CREATED)
def create_asset(
    payload: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    asset = Asset(
        user_id=current_user.id,
        asset_class=payload.asset_class,
        code=payload.code.upper().strip(),
        name=payload.name.strip(),
        quantity=payload.quantity,
        amount_invested=payload.amount_invested,
        purchase_date=payload.purchase_date,
    )
    try:
        db.add(asset)
        db.commit()
        db.refresh(asset)
    except SQLAlchemyError:
        db.rollback()
        # O detalhe técnico vai para o terminal do back-end; a tela mostra um
        # texto claro (em vez de um "erro 500" sem explicação).
        logger.exception("Falha ao salvar o ativo no banco de dados")
        raise HTTPException(
            status_code=500,
            detail="Não foi possível salvar no banco de dados. Veja a mensagem no terminal do back-end.",
        )
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(
    asset_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    asset = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.user_id == current_user.id)
        .first()
    )
    # Importante: o filtro por user_id acima garante que um usuário nunca
    # consiga apagar ativo de outra pessoa, mesmo sabendo o id.
    if asset is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado.")

    db.delete(asset)
    db.commit()
