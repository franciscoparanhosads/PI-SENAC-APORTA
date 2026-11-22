/**
 * Funções utilitárias compartilhadas pelas telas do protótipo.
 *
 * Carregado em todas as páginas antes do script específico de cada tela.
 */
const CLASS_LABELS = {
  renda_fixa: "Renda Fixa",
  fii: "FIIs",
  acao: "Ações",
  cripto: "Cripto",
};

/**
 * Escapa caracteres especiais de HTML. Use SEMPRE que um texto vindo do
 * usuário ou da API for inserido via innerHTML — sem isso, um nome de ativo
 * como `<img src=x onerror=alert(1)>` seria executado como código (XSS).
 */
function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatBRL(value, casasDecimais = 2) {
  return value.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: casasDecimais,
    maximumFractionDigits: casasDecimais,
  });
}

function initials(name) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

function formatarData(isoDate) {
  const [year, month, day] = isoDate.split("-");
  return `${day}/${month}/${year}`;
}

/** Data de hoje no fuso do navegador, no formato AAAA-MM-DD (para <input type="date">).
 *  Não usar `valueAsDate = new Date()`: ele usa UTC e, à noite no Brasil, já
 *  mostra a data de amanhã. */
function hojeISO() {
  const d = new Date();
  const mes = String(d.getMonth() + 1).padStart(2, "0");
  const dia = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${mes}-${dia}`;
}

/**
 * Máscara de moeda para campos de texto: enquanto o usuário digita, o campo
 * ganha os pontos de milhar e aceita a vírgula para os centavos.
 * Ex.: digitar 5000 mostra 5.000; digitar 5000,5 mostra 5.000,5.
 */
function formatarNumeroInput(valor) {
  return Number(valor).toLocaleString("pt-BR", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

/** Converte o texto do campo ("5.000,50") em número (5000.5). Vazio vira 0. */
function lerMoeda(texto) {
  const numero = parseFloat(String(texto).replace(/\./g, "").replace(",", "."));
  return Number.isFinite(numero) ? numero : 0;
}

/** Formata o texto digitado: pontos de milhar na parte inteira e até 2 casas depois da vírgula. */
function mascararMoeda(texto) {
  const temVirgula = texto.includes(",");
  const [inteiroBruto, ...resto] = texto.replace(/[^\d,]/g, "").split(",");
  const inteiro = inteiroBruto.replace(/^0+(?=\d)/, "").slice(0, 11); // sem zeros à esquerda
  const comMilhar = inteiro.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  if (!temVirgula) return comMilhar;
  const centavos = resto.join("").slice(0, 2);
  return `${comMilhar || "0"},${centavos}`;
}

function aplicarMascaraMoeda(input) {
  input.addEventListener("input", () => {
    // guarda quantos dígitos/vírgula havia antes do cursor, para não pular o cursor para o fim
    const antes = input.value.slice(0, input.selectionStart ?? input.value.length);
    const posicao = antes.replace(/[^\d,]/g, "").length;

    input.value = mascararMoeda(input.value);

    let contados = 0;
    let novaPosicao = input.value.length;
    if (posicao === 0) novaPosicao = 0;
    else {
      for (let k = 0; k < input.value.length; k++) {
        if (/[\d,]/.test(input.value[k])) contados++;
        if (contados === posicao) { novaPosicao = k + 1; break; }
      }
    }
    input.setSelectionRange(novaPosicao, novaPosicao);
  });

  // ao sair do campo, completa os centavos (5.000 vira 5.000,00)
  input.addEventListener("blur", () => {
    if (input.value) input.value = formatarNumeroInput(lerMoeda(input.value));
  });
}

/** Preenche o avatar com as iniciais do usuário e faz o botão "Sair" encerrar a sessão.
 *  Tolerante a falhas: se algum elemento da barra não existir, o resto da tela
 *  (carregar ativos, painel etc.) continua funcionando. */
function setupTopbar() {
  const user = getUserInfo();
  const avatar = document.getElementById("avatar");
  if (avatar && user) avatar.textContent = initials(user.userName);

  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      clearSession();
      window.location.href = "index.html";
    });
  }
  return user;
}
