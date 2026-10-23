"""
Popula o banco de dados com as 3 personas do projeto (Juliana, Miguel e
Jéssica) e seus ativos de exemplo, para a demonstração do protótipo.

Rodar com:  python seed.py

Pode ser executado mais de uma vez: se o e-mail já existir, aquela persona é
pulada (não duplica os dados).
"""
from datetime import date

from auth import hash_password
from database import Base, SessionLocal, engine
from models import Asset, User

# ATENÇÃO: senhas simples de propósito — servem só para a demonstração deste
# protótipo acadêmico.
PERSONAS = [
    {
        "name": "Juliana Souza",
        "email": "juliana@aporta.com",
        "password": "juliana123",
        "persona": "iniciante",
        "assets": [
            dict(
                asset_class="renda_fixa",
                code="TESOURO-SELIC-2029",
                name="Tesouro Selic 2029",
                quantity=1,
                amount_invested=8000.00,
                purchase_date=date(2025, 3, 12),
            ),
            dict(
                asset_class="fii",
                code="HGLG11",
                name="CSHG Logística FII",
                quantity=20,
                amount_invested=2500.00,
                purchase_date=date(2025, 8, 4),
            ),
        ],
    },
    {
        "name": "Miguel Almeida",
        "email": "miguel@aporta.com",
        "password": "miguel123",
        "persona": "intermediário",
        "assets": [
            dict(
                asset_class="renda_fixa",
                code="CDB-BANCO-ALFA",
                name="CDB Banco Alfa — 112% CDI",
                quantity=1,
                amount_invested=15000.00,
                purchase_date=date(2024, 11, 20),
            ),
            dict(
                asset_class="acao",
                code="PETR4",
                name="Petrobras PN",
                quantity=50,
                amount_invested=1900.00,
                purchase_date=date(2025, 1, 15),
            ),
            dict(
                asset_class="acao",
                code="VALE3",
                name="Vale ON",
                quantity=30,
                amount_invested=1780.00,
                purchase_date=date(2025, 4, 2),
            ),
            dict(
                asset_class="fii",
                code="HGLG11",
                name="CSHG Logística FII",
                quantity=40,
                amount_invested=6800.00,
                purchase_date=date(2025, 6, 18),
            ),
        ],
    },
    {
        "name": "Jéssica Mendes",
        "email": "jessica@aporta.com",
        "password": "jessica123",
        "persona": "avançado",
        "assets": [
            dict(
                asset_class="renda_fixa",
                code="TESOURO-IPCA-2035",
                name="Tesouro IPCA+ 2035",
                quantity=1,
                amount_invested=40000.00,
                purchase_date=date(2023, 5, 10),
            ),
            dict(
                asset_class="acao",
                code="ITUB4",
                name="Itaú Unibanco PN",
                quantity=300,
                amount_invested=9930.00,
                purchase_date=date(2024, 2, 22),
            ),
            dict(
                asset_class="acao",
                code="MGLU3",
                name="Magazine Luiza ON",
                quantity=500,
                amount_invested=4600.00,
                purchase_date=date(2024, 9, 9),
            ),
            dict(
                asset_class="fii",
                code="HGLG11",
                name="CSHG Logística FII",
                quantity=100,
                amount_invested=17000.00,
                purchase_date=date(2024, 7, 1),
            ),
            dict(
                asset_class="cripto",
                code="BTC",
                name="Bitcoin",
                quantity=0.05,
                amount_invested=15000.00,
                purchase_date=date(2025, 2, 14),
            ),
        ],
    },
]


def run_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for persona in PERSONAS:
            existing = db.query(User).filter(User.email == persona["email"]).first()
            if existing:
                print(f"- {persona['email']} já existe, pulando.")
                continue

            user = User(
                name=persona["name"],
                email=persona["email"],
                password_hash=hash_password(persona["password"]),
                persona=persona["persona"],
            )
            db.add(user)
            db.flush()  # garante o user.id antes de criar os ativos

            for asset_data in persona["assets"]:
                db.add(Asset(user_id=user.id, **asset_data))

            print(f"+ Criado(a): {persona['name']} <{persona['email']}>")

        db.commit()
        print("\nSeed concluído. Credenciais de teste:")
        for persona in PERSONAS:
            print(f"  {persona['email']} / {persona['password']}  ({persona['persona']})")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
