/**
 * Camada central de chamadas à API do protótipo.
 *
 * Todo fetch passa por aqui: adiciona o token JWT automaticamente e trata a
 * resposta 401 (sessão expirada/token inválido) mandando o usuário de volta
 * para o login. Nenhuma outra tela deve montar `fetch` na mão.
 */

const API_BASE_URL = window.location.port === "8000" ? "" : "http://localhost:8000";

function getToken() {
  return sessionStorage.getItem("aporta_token");
}

function getUserInfo() {
  const raw = sessionStorage.getItem("aporta_user");
  return raw ? JSON.parse(raw) : null;
}

function saveSession(token, userName, persona) {
  sessionStorage.setItem("aporta_token", token);
  sessionStorage.setItem("aporta_user", JSON.stringify({ userName, persona }));
}

function clearSession() {
  sessionStorage.removeItem("aporta_token");
  sessionStorage.removeItem("aporta_user");
}

/** Devolve true se há sessão; senão redireciona para o login e devolve false
 *  (quem chama deve parar a execução, para não disparar chamadas à API). */
function requireAuthOrRedirect() {
  if (!getToken()) {
    window.location.href = "index.html";
    return false;
  }
  return true;
}

async function apiRequest(path, { method = "GET", body = null, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401) {
    clearSession();
    window.location.href = "index.html";
    throw new Error("Sessão expirada. Faça login novamente.");
  }

  if (!response.ok) {
    let detail = "Ocorreu um erro ao falar com o servidor.";
    try {
      const errorBody = await response.json();
      detail = errorBody.detail || detail;
    } catch (_) {
      /* resposta sem corpo JSON — mantém a mensagem padrão */
    }
    throw new Error(detail);
  }

  if (response.status === 204) return null;
  return response.json();
}

const Api = {
  login: (email, password) =>
    apiRequest("/login", { method: "POST", body: { email, password }, auth: false }),
  listAssets: () => apiRequest("/assets"),
  createAsset: (asset) => apiRequest("/assets", { method: "POST", body: asset }),
  deleteAsset: (id) => apiRequest(`/assets/${id}`, { method: "DELETE" }),
  getQuotes: () => apiRequest("/quotes"),
  simulate: (payload) => apiRequest("/simulate", { method: "POST", body: payload }),
};
