"""Cria o .env a partir do .env.example com uma JWT_SECRET_KEY aleatória.
Não sobrescreve um .env que já exista."""
import secrets
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ENV, EXEMPLO = AQUI / ".env", AQUI / ".env.example"


def gerar_env() -> bool:
    if ENV.exists():
        return False
    linhas = []
    for linha in EXEMPLO.read_text(encoding="utf-8").splitlines():
        if linha.startswith("JWT_SECRET_KEY="):
            linha = f"JWT_SECRET_KEY={secrets.token_urlsafe(48)}"
        linhas.append(linha)
    ENV.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return True


if __name__ == "__main__":
    print("Arquivo .env criado." if gerar_env() else "Arquivo .env já existe.")
