let chartInstance = null;

document.addEventListener("DOMContentLoaded", async () => {
  if (!requireAuthOrRedirect()) return;
  setupTopbar();

  await preencherPatrimonioAtual();

  document.getElementById("sim-form").addEventListener("submit", onSimulate);
});

async function preencherPatrimonioAtual() {
  try {
    const [assets, quotes] = await Promise.all([Api.listAssets(), Api.getQuotes()]);
    const quoteByCode = {};
    quotes.forEach((q) => { quoteByCode[q.code] = q; });

    let total = 0;
    assets.forEach((asset) => {
      const quote = quoteByCode[asset.code];
      const price = quote ? quote.price : asset.amount_invested / asset.quantity;
      total += price * asset.quantity;
    });

    document.getElementById("current_amount").value = total.toFixed(2);
    // meta padrão sugerida: 5x o patrimônio atual (ou R$ 500.000 se ainda não tem nada)
    const metaSugerida = total > 0 ? total * 5 : 500000;
    document.getElementById("goal_amount").value = metaSugerida.toFixed(2);
    document.getElementById("monthly_contribution").value = (total * 0.02 || 500).toFixed(2);
  } catch (_) {
    /* se falhar, o usuário simplesmente preenche os campos manualmente */
  }
}

async function onSimulate(event) {
  event.preventDefault();
  const errorBox = document.getElementById("sim-error");
  const avisoBox = document.getElementById("aviso-nao-alcancavel");
  const submitBtn = document.getElementById("sim-btn");
  errorBox.textContent = "";
  avisoBox.textContent = "";

  const payload = {
    current_amount: parseFloat(document.getElementById("current_amount").value),
    monthly_contribution: parseFloat(document.getElementById("monthly_contribution").value),
    annual_return_rate: parseFloat(document.getElementById("annual_return_rate").value),
    goal_amount: parseFloat(document.getElementById("goal_amount").value),
  };

  submitBtn.disabled = true;
  submitBtn.textContent = "Calculando...";

  try {
    const result = await Api.simulate(payload);
    renderResultado(result, payload.goal_amount);
  } catch (err) {
    errorBox.textContent = err.message || "Não foi possível calcular a simulação.";
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Calcular projeção";
  }
}

function renderResultado(result, goalAmount) {
  const tempoEl = document.getElementById("resultado-tempo");
  const metaEl = document.getElementById("resultado-meta");
  const avisoBox = document.getElementById("aviso-nao-alcancavel");

  metaEl.textContent = formatBRL(goalAmount, 0);

  if (!result.reachable) {
    tempoEl.textContent = "mais de 50 anos";
    avisoBox.textContent =
      "Com esses valores, a meta não é alcançada em até 50 anos. Tente aumentar o aporte mensal ou a taxa de retorno.";
  } else if (result.months_to_goal === 0) {
    tempoEl.textContent = "Você já atingiu sua meta!";
  } else {
    const partes = [];
    if (result.years > 0) partes.push(`${result.years} ano${result.years === 1 ? "" : "s"}`);
    if (result.months > 0) partes.push(`${result.months} ${result.months === 1 ? "mês" : "meses"}`);
    tempoEl.textContent = partes.join(" e ") || "menos de 1 mês";
  }

  renderGraficoLinha(result.projection, goalAmount);
}

function renderGraficoLinha(projection, goalAmount) {
  const canvas = document.getElementById("grafico-linha");
  const labels = projection.map((p) => `${(p.month / 12).toFixed(1)}a`);
  const valores = projection.map((p) => p.amount);

  if (chartInstance) chartInstance.destroy();

  chartInstance = new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Patrimônio projetado",
          data: valores,
          borderColor: "#1F6B4D",
          backgroundColor: "rgba(31,107,77,0.08)",
          borderWidth: 3,
          pointRadius: 0,
          fill: true,
          tension: 0.25,
        },
        {
          label: "Meta",
          data: valores.map(() => goalAmount),
          borderColor: "#B8935B",
          borderDash: [6, 6],
          borderWidth: 2,
          pointRadius: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: true, position: "bottom" } },
      scales: {
        y: { ticks: { callback: (v) => formatBRL(v, 0) } },
      },
    },
  });
}
