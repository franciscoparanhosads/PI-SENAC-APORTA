"""
Autenticação: hash de senha com bcrypt e emissão/validação de tokens JWT.

- Senhas: nunca ficam em texto puro. `hash_password` gera o hash salvo no banco;
  `verify_password` compara o texto digitado com esse hash no login.
- JWT: carrega o id e a persona do usuário, assina com JWT_SECRET_KEY e expira
  em JWT_EXPIRE_MINUTES (padrão 120 min / 2h).
"""
import os
import warnings
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models import User

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "").strip()
if not JWT_SECRET_KEY:
    # Sem .env, os tokens seriam assinados com uma chave pública e conhecida.
    # Seguimos funcionando (é um protótipo), mas avisamos alto no terminal.
    warnings.warn(
        "JWT_SECRET_KEY não definida no .env — usando uma chave de desenvolvimento "
        "insegura. Copie .env.example para .env e defina uma chave aleatória.",
        stacklevel=1,
    )
    JWT_SECRET_KEY = "dev-only-change-me"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Dependency usada em toda rota protegida: exige um JWT válido no header
    Authorization: Bearer <token> e devolve o usuário correspondente."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user
