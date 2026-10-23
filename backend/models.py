"""
Modelos SQLAlchemy — refletem as tabelas `users` e `assets`.
"""
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    # Nunca armazenamos a senha em texto puro — só o hash bcrypt.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    persona: Mapped[str] = mapped_column(String(30), nullable=False)  # iniciante / intermediário / avançado
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    assets: Mapped[list["Asset"]] = relationship(
        "Asset", back_populates="owner", cascade="all, delete-orphan"
    )


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # classe: renda_fixa | fii | acao | cripto
    asset_class: Mapped[str] = mapped_column("class", String(20), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    amount_invested: Mapped[float] = mapped_column(Float, nullable=False)
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="assets")
