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

function logout() {
  clearSession();                        // apaga aporta_token e aporta_user
  window.location.replace("index.html"); // replace: o "voltar" não retorna ao painel
}

/** Preenche o avatar com as iniciais do usuário e liga o botão "Sair". */
function setupTopbar() {
  const user = getUserInfo();
  const avatarBtn = document.getElementById("avatar-btn");
  if (user) avatarBtn.textContent = initials(user.userName);
  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) logoutBtn.addEventListener("click", logout);
  return user;
}
