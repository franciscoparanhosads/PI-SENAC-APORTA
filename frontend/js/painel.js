const CLASS_COLORS = {
  renda_fixa: "#1F6B4D",
  fii: "#B8935B",
  acao: "#3B5BA5",
  cripto: "#A2483D",
};

document.addEventListener("DOMContentLoaded", async () => {
  if (!requireAuthOrRedirect()) return;

  const user = setupTopbar();
  if (user) {
    document.getElementById("saudacao").textContent =
      `Olá, ${user.userName.split(" ")[0]} — aqui está o resumo do seu patrimônio.`;
  }

  try {
    const [assets, quotes] = await Promise.all([Api.listAssets(), Api.getQuotes()]);
    renderPainel(assets, quotes);
  } catch (err) {
    document.getElementById("ativos-tbody").innerHTML =
      `<tr><td colspan="4" class="empty-state">Não foi possível carregar os dados: ${escapeHtml(err.message)}</td></tr>`;
  }
});

function renderPainel(assets, quotes) {
  // Uma cotação por ativo cadastrado (não por código): dois aportes no mesmo
  // ativo simulado têm preços-base diferentes e não podem compartilhar cotação.
  const quoteByAssetId = {};
  quotes.forEach((q) => { quoteByAssetId[q.asset_id] = q; });

  let total = 0;
  let totalInvested = 0;
  const totalsByClass = { renda_fixa: 0, fii: 0, acao: 0, cripto: 0 };

  const enriched = assets.map((asset) => {
    const quote = quoteByAssetId[asset.id];
    const priceNow = quote ? quote.price : asset.amount_invested / asset.quantity;
    const currentValue = priceNow * asset.quantity;
    total += currentValue;
    totalInvested += asset.amount_invested;
    totalsByClass[asset.asset_class] += currentValue;
    return { ...asset, currentValue, quote };
  });

  document.getElementById("patrimonio-total").textContent = formatBRL(total);

  const pill = document.getElementById("pill-status");
  const changePct = totalInvested > 0 ? ((total - totalInvested) / totalInvested) * 100 : 0;
  pill.textContent = `${changePct >= 0 ? "+" : ""}${changePct.toFixed(1)}% desde o aporte`;
  pill.style.color = changePct >= 0 ? "var(--accent)" : "var(--rust)";
  pill.style.background = changePct >= 0 ? "var(--accent-soft)" : "#F5E6E3";

  renderDonut(totalsByClass, total);
  renderLegenda(totalsByClass, total);
  renderTabela(enriched);
}

function renderDonut(totalsByClass, total) {
  const canvas = document.getElementById("grafico-donut");
  const labels = Object.keys(totalsByClass).filter((k) => totalsByClass[k] > 0);

  if (total === 0 || labels.length === 0) {
    canvas.parentElement.innerHTML = '<p class="empty-state" style="padding:0;">Cadastre um ativo para ver o gráfico.</p>';
    return;
  }

  new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: labels.map((k) => CLASS_LABELS[k]),
      datasets: [{
        data: labels.map((k) => totalsByClass[k]),
        backgroundColor: labels.map((k) => CLASS_COLORS[k]),
        borderWidth: 0,
      }],
    },
    options: {
      cutout: "62%",
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
    },
  });
}

function renderLegenda(totalsByClass, total) {
  const container = document.getElementById("legenda-container");
  container.innerHTML = "";

  Object.keys(CLASS_LABELS).forEach((key) => {
    const value = totalsByClass[key];
    if (value <= 0) return;
    const pct = total > 0 ? (value / total) * 100 : 0;

    const row = document.createElement("div");
    row.className = "legenda-item";
    row.innerHTML = `
      <div class="legenda-esq">
        <div class="dot" style="background:${CLASS_COLORS[key]};"></div>
        <span style="font-size:14px;">${CLASS_LABELS[key]}</span>
      </div>
      <span style="font-size:14px; font-weight:700;">${pct.toFixed(0)}% · ${formatBRL(value)}</span>
    `;
    container.appendChild(row);
  });
}

function renderTabela(enriched) {
  const tbody = document.getElementById("ativos-tbody");

  if (enriched.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="empty-state">Você ainda não cadastrou nenhum ativo. <a href="cadastro.html">Adicionar agora</a>.</td></tr>`;
    return;
  }

  // Nome e quantidade vêm do usuário: passam por escapeHtml antes do innerHTML.
  tbody.innerHTML = enriched
    .map((asset) => {
      const tag = asset.quote?.is_real_time
        ? '<span class="tag-real">tempo real</span>'
        : '<span class="tag-mock">simulado</span>';
      return `
        <tr>
          <td><strong>${escapeHtml(asset.name)}</strong><br>${tag}</td>
          <td style="color: var(--ink-muted);">${CLASS_LABELS[asset.asset_class]}</td>
          <td>${escapeHtml(asset.quantity.toLocaleString("pt-BR"))}</td>
          <td style="font-weight:700;">${formatBRL(asset.currentValue)}</td>
        </tr>
      `;
    })
    .join("");
}
