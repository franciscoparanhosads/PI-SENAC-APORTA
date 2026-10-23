document.addEventListener("DOMContentLoaded", () => {
  // Se já existe uma sessão válida, pula direto para o painel.
  if (getToken()) {
    window.location.href = "painel.html";
    return;
  }

  const form = document.getElementById("login-form");
  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const errorBox = document.getElementById("login-error");
  const submitBtn = document.getElementById("login-btn");

  document.querySelectorAll(".persona-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      emailInput.value = btn.dataset.email;
      passwordInput.value = btn.dataset.password;
    });
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorBox.textContent = "";
    submitBtn.disabled = true;
    submitBtn.textContent = "Entrando...";

    try {
      const result = await Api.login(emailInput.value.trim(), passwordInput.value);
      saveSession(result.access_token, result.user_name, result.persona);
      window.location.href = "painel.html";
    } catch (err) {
      errorBox.textContent = err.message || "Não foi possível entrar. Tente novamente.";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Entrar";
    }
  });
});
