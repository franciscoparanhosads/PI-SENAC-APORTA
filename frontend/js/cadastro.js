const REAL_TIME_TICKERS = ["PETR4", "MGLU3", "VALE3", "ITUB4"];

let classeSelecionada = "renda_fixa";

document.addEventListener("DOMContentLoaded", () => {
  if (!requireAuthOrRedirect()) return;
  setupTopbar();

  document.getElementById("purchase_date").value = hojeISO();

  document.querySelectorAll(".class-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      document.querySelectorAll(".class-chip").forEach((c) => c.classList.remove("selected"));
      chip.classList.add("selected");
      classeSelecionada = chip.dataset.classe;
    });
  });

  const codeInput = document.getElementById("code");
  const dica = document.getElementById("dica-tickers");
  codeInput.addEventListener("input", () => {
    const code = codeInput.value.trim().toUpperCase();
    if (REAL_TIME_TICKERS.includes(code)) {
      dica.textContent = `"${code}" tem cotação em tempo real via brapi.dev.`;
      dica.style.color = "var(--accent)";
    } else {
      dica.textContent = "Este código receberá uma cotação simulada (não é um dos 4 tickers em tempo real).";
      dica.style.color = "var(--ink-faint)";
    }
  });

  document.getElementById("asset-form").addEventListener("submit", onSubmit);

  carregarAtivos();
});

async function onSubmit(event) {
  event.preventDefault();
  const errorBox = document.getElementById("form-error");
  const successBox = document.getElementById("form-success");
  const submitBtn = document.getElementById("submit-btn");
  errorBox.textContent = "";
  successBox.textContent = "";

  const payload = {
    asset_class: classeSelecionada,
    code: document.getElementById("code").value.trim(),
    name: document.getElementById("name").value.trim(),
    quantity: parseFloat(document.getElementById("quantity").value),
    amount_invested: parseFloat(document.getElementById("amount").value),
    purchase_date: document.getElementById("purchase_date").value,
  };

  submitBtn.disabled = true;
  submitBtn.textContent = "Adicionando...";

  try {
    await Api.createAsset(payload);
    successBox.textContent = "Ativo adicionado com sucesso!";
    document.getElementById("asset-form").reset();
    document.getElementById("purchase_date").value = hojeISO();
    await carregarAtivos();
  } catch (err) {
    errorBox.textContent = err.message || "Não foi possível adicionar o ativo.";
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Adicionar à carteira";
  }
}

async function carregarAtivos() {
  const container = document.getElementById("lista-ativos");
  const contador = document.getElementById("contador-ativos");
  try {
    const assets = await Api.listAssets();
    contador.textContent = `${assets.length} ativo${assets.length === 1 ? "" : "s"}`;

    if (assets.length === 0) {
      container.innerHTML = '<p class="empty-state" style="padding:0;">Nenhum ativo cadastrado ainda.</p>';
      return;
    }

    // Todo texto digitado pelo usuário passa por escapeHtml antes de ir para o innerHTML.
    container.innerHTML = assets
      .map(
        (asset) => `
        <div class="item-cadastrado">
          <div style="display:flex; flex-direction:column;">
            <span style="font-size:14px; font-weight:700;">${escapeHtml(asset.name)}</span>
            <span style="font-size:12px; color: var(--ink-muted);">${escapeHtml(asset.code)} · ${CLASS_LABELS[asset.asset_class]} · aportado em ${formatarData(asset.purchase_date)}</span>
          </div>
          <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px;">
            <span style="font-size:14px; font-weight:700;">${formatBRL(asset.amount_invested)}</span>
            <button class="btn-remover" data-id="${asset.id}">remover</button>
          </div>
        </div>
      `
      )
      .join("");

    container.querySelectorAll(".btn-remover").forEach((btn) => {
      btn.addEventListener("click", async () => {
        btn.textContent = "removendo...";
        try {
          await Api.deleteAsset(btn.dataset.id);
          await carregarAtivos();
        } catch (err) {
          alert(err.message || "Não foi possível remover o ativo.");
          btn.textContent = "remover";
        }
      });
    });
  } catch (err) {
    container.innerHTML = `<p class="empty-state" style="padding:0;">Erro ao carregar: ${escapeHtml(err.message)}</p>`;
  }
}
