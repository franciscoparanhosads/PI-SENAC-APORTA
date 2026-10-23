"""
 Configuração da conexão com o banco de dados SQLite via SQLAlchemy.

Todo acesso ao banco passa pelo ORM (nunca SQL concatenado manualmente),
o que já evita SQL Injection por construção.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aporta.db")

# check_same_thread=False é necessário para o SQLite funcionar com o FastAPI
# (que pode acessar o banco a partir de threads diferentes).
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI: abre uma sessão por requisição e sempre fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
