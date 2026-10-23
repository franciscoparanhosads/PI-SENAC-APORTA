"""Testes do simulador de independência financeira."""
import pytest


def simular(client, headers, **valores):
    payload = {
        "current_amount": 0,
        "monthly_contribution": 1000,
        "annual_return_rate": 10,
        "goal_amount": 100000,
    }
    payload.update(valores)
    return client.post("/simulate", json=payload, headers=headers)


def meses_pela_formula(pv, pmt, taxa_anual_pct, meta):
    """Conta independente do back-end, usando a fórmula fechada de juros compostos
    FV = PV·(1+i)^n + PMT·((1+i)^n − 1)/i — serve de "gabarito" para o teste."""
    i = (1 + taxa_anual_pct / 100) ** (1 / 12) - 1
    n = 0
    while True:
        n += 1
        fv = pv * (1 + i) ** n + pmt * ((1 + i) ** n - 1) / i
        if fv >= meta:
            return n


def test_taxa_quase_zero_vira_soma_simples_dos_aportes(client, ana):
    """Com juros praticamente zero, 12 aportes de R$ 1.000 chegam a R$ 12.000
    em exatamente 1 ano — fácil de conferir de cabeça."""
    resposta = simular(
        client, ana["headers"],
        current_amount=0, monthly_contribution=1000, annual_return_rate=0.000001, goal_amount=12000,
    )

    corpo = resposta.json()
    assert resposta.status_code == 200
    assert corpo["reachable"] is True
    assert corpo["months_to_goal"] == 12
    assert corpo["years"] == 1
    assert corpo["months"] == 0


@pytest.mark.parametrize(
    "pv, pmt, taxa, meta",
    [
        (1000, 500, 10, 20000),
        (0, 300, 9.5, 50000),
        (25000, 1500, 12, 1000000),
    ],
)
def test_resultado_bate_com_a_formula_de_juros_compostos(client, ana, pv, pmt, taxa, meta):
    corpo = simular(
        client, ana["headers"],
        current_amount=pv, monthly_contribution=pmt, annual_return_rate=taxa, goal_amount=meta,
    ).json()

    esperado = meses_pela_formula(pv, pmt, taxa, meta)
    assert corpo["months_to_goal"] == esperado
    assert corpo["years"] * 12 + corpo["months"] == esperado


def test_meta_ja_atingida_retorna_zero_meses(client, ana):
    corpo = simular(client, ana["headers"], current_amount=5000, goal_amount=1000).json()

    assert corpo["reachable"] is True
    assert corpo["months_to_goal"] == 0
    assert corpo["projection"] == [{"month": 0, "amount": 5000}]


def test_meta_inalcancavel_em_50_anos(client, ana):
    corpo = simular(client, ana["headers"], current_amount=0, monthly_contribution=0, goal_amount=1000).json()

    assert corpo["reachable"] is False
    assert corpo["months_to_goal"] is None
    assert corpo["years"] is None


def test_projecao_comeca_no_patrimonio_atual_e_termina_na_meta(client, ana):
    corpo = simular(client, ana["headers"], current_amount=2000, goal_amount=30000).json()
    projecao = corpo["projection"]

    assert projecao[0] == {"month": 0, "amount": 2000}
    assert projecao[-1]["month"] == corpo["months_to_goal"]
    assert projecao[-1]["amount"] >= 30000
    # o patrimônio só cresce mês a mês
    valores = [p["amount"] for p in projecao]
    assert valores == sorted(valores)


@pytest.mark.parametrize(
    "campo, valor_invalido",
    [
        ("annual_return_rate", 0),
        ("annual_return_rate", 150),
        ("monthly_contribution", -100),
        ("current_amount", -1),
        ("goal_amount", 0),
    ],
)
def test_valores_invalidos_sao_rejeitados(client, ana, campo, valor_invalido):
    resposta = simular(client, ana["headers"], **{campo: valor_invalido})
    assert resposta.status_code == 422
