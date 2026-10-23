from fastapi import APIRouter, Depends

from auth import get_current_user
from models import User
from schemas import SimulationPoint, SimulationRequest, SimulationResponse

router = APIRouter(prefix="/simulate", tags=["simulator"])

# Limite de segurança: se em 50 anos (600 meses) a meta não for atingida,
# paramos de simular e avisamos que o cenário não é alcançável assim.
MAX_MONTHS = 600


@router.post("", response_model=SimulationResponse)
def simulate(
    payload: SimulationRequest, current_user: User = Depends(get_current_user)
):
    """
    Projeta a evolução do patrimônio mês a mês com aportes constantes, usando
    juros compostos, até atingir a meta (ou até o limite de segurança).

    FV = PV × (1 + i)^n + PMT × [((1 + i)^n − 1) / i]

    Aqui aplicamos essa fórmula mês a mês (iterativamente) em vez de resolver
    para n analiticamente — mais simples de ler e de explicar na apresentação.
    """
    pv = payload.current_amount
    pmt = payload.monthly_contribution
    goal = payload.goal_amount
    annual_rate = payload.annual_return_rate / 100

    # taxa mensal equivalente à taxa anual informada
    monthly_rate = (1 + annual_rate) ** (1 / 12) - 1

    projection: list[SimulationPoint] = [SimulationPoint(month=0, amount=round(pv, 2))]

    amount = pv
    reached_month = None

    if amount >= goal:
        reached_month = 0
    else:
        for month in range(1, MAX_MONTHS + 1):
            amount = amount * (1 + monthly_rate) + pmt
            # guardamos só 1 ponto a cada 3 meses para o gráfico não ficar
            # pesado, sempre incluindo o mês em que a meta foi atingida
            if month % 3 == 0 or amount >= goal:
                projection.append(SimulationPoint(month=month, amount=round(amount, 2)))
            if amount >= goal:
                reached_month = month
                break

    if reached_month is None:
        return SimulationResponse(
            reachable=False,
            months_to_goal=None,
            years=None,
            months=None,
            projection=projection,
        )

    years = reached_month // 12
    months = reached_month % 12
    return SimulationResponse(
        reachable=True,
        months_to_goal=reached_month,
        years=years,
        months=months,
        projection=projection,
    )
