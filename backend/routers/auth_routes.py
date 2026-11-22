from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import DUMMY_PASSWORD_HASH, create_access_token, verify_password
from database import get_db
from models import User
from schemas import LoginRequest, TokenResponse

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    # Mensagem de erro genérica de propósito: não revelamos se foi o e-mail
    # ou a senha que estava errada (evita enumeração de usuários cadastrados).
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="E-mail ou senha inválidos.",
    )

    # Se o e-mail não existe, verificamos a senha contra um hash falso só para
    # gastar o mesmo tempo (o bcrypt é lento de propósito). Sem isso, o tempo de
    # resposta revelaria quais e-mails estão cadastrados.
    password_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
    password_ok = verify_password(payload.password, password_hash)

    if user is None or not password_ok:
        raise invalid_credentials

    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user_name=user.name, persona=user.persona)
