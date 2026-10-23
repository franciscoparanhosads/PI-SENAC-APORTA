# Notas de atualização

Registro das mudanças do protótipo Aporta.

---

## Versão 0.2.0 — 23/10/2026

Revisão geral do protótipo: correções de segurança e de bugs, suporte a celular,
instalação automática no Windows e testes automatizados.

### 🔒 Segurança

- **Corrigida falha de XSS (Cross-Site Scripting).** O nome do ativo era inserido
  na página sem tratamento. Um ativo cadastrado com o nome
  `<img src=x onerror=alert(1)>` executava código no navegador. Agora todo
  texto vindo do usuário passa pela função `escapeHtml` antes de aparecer na
  tela (`frontend/js/utils.js`).
- Corrigido o comentário em `schemas.py`, que dizia que a validação do Pydantic
  impedia XSS. Ela valida só tipo e tamanho; a proteção fica no front-end.
- O back-end agora **avisa no terminal** quando o `.env` não tem a
  `JWT_SECRET_KEY`. Antes ele usava uma chave padrão sem avisar ninguém.
- CORS: desligado o `allow_credentials`, que não era necessário (o token vai no
  header `Authorization`, não em cookies).

### 🐛 Correções de bugs

- **Cotação marcada errado como "tempo real".** Quando a brapi.dev estava fora do
  ar, o preço reserva (fixo ou do cache vencido) aparecia como "tempo real".
  Agora aparece como "simulado".
- **Data do aporte errada à noite.** O campo de data usava o horário UTC e, depois
  das 21h no horário de Brasília, já vinha com a data de amanhã. Agora usa a data
  local do navegador.
- **Script de instalação inexistente.** O `iniciar-tudo.bat` mandava rodar o
  `backend\instalar.bat`, que não existia. O arquivo foi criado.
- **Instalação falhava no Python 3.14.** O `pydantic==2.9.2` não tem versão para o
  Python 3.14, e o `pip install` quebrava. As dependências foram atualizadas
  (FastAPI 0.120, Pydantic 2.12, SQLAlchemy 2.0.44, entre outras).
- As páginas internas agora param antes de chamar a API quando não há login,
  em vez de disparar requisições que seriam recusadas.

### 📱 Layout para celular

- Nenhuma tela rola mais para o lado em telas pequenas (testado em 375px).
- Login: o painel escuro vira um cabeçalho em cima do formulário.
- Painel: as colunas ficam empilhadas e a tabela de ativos esconde a coluna
  "Classe" (a informação continua no gráfico).
- Topbar mais compacta, com espaçamentos menores em todas as telas.

### ⚙️ Instalação e uso

- **Novo `backend\instalar.bat`:** cria o ambiente virtual, instala as
  dependências, gera o `.env` e popula o banco com as 3 personas, tudo com dois
  cliques.
- **Novo `backend\rodar-testes.bat`:** roda os testes automatizados.
- README com a nova seção "Jeito rápido (Windows)".

### ✅ Testes automatizados (novo)

48 testes com `pytest` na pasta `backend/tests/`. Eles usam um banco temporário
(o `aporta.db` não é alterado) e não acessam a internet.

| Arquivo | Testes | O que verifica |
|---|---|---|
| `test_auth.py` | 13 | Login, senha salva só como hash, bloqueio de rotas sem token ou com token inválido, expirado ou falsificado |
| `test_assets.py` | 17 | Criar, listar e remover ativos; rejeição de dados inválidos; um usuário não acessa nem apaga ativos de outro |
| `test_simulator.py` | 12 | Resultado confere com a fórmula de juros compostos; meta já atingida, inalcançável e valores inválidos |
| `test_quotes.py` | 6 | Cotação real, cache, preço reserva quando a brapi.dev cai e variação da cotação simulada |

### 🧹 Organização do código

- Funções repetidas em 3 arquivos JS (`initials`, `formatBRL`, `formatarData`,
  rótulos das classes e o botão de sair) foram reunidas em
  `frontend/js/utils.js`.
- Atualizado o código que usava recursos obsoletos: `class Config` do Pydantic
  virou `model_config = ConfigDict(...)`, e `datetime.utcnow` virou
  `datetime.now(timezone.utc)`.

### 📌 Pendências conhecidas

- Valores em dinheiro ainda são `Float`; o ideal seria `Decimal`.
- Não há tela de cadastro de novos usuários (só as 3 personas do seed) nem de
  edição de ativos.
- A cotação simulada muda a cada recarregamento da página.

---

## Versão 0.1.0 — 21/09/2026

Primeira versão do protótipo: login com JWT, painel de alocação patrimonial,
cadastro de ativos, cotações (reais para PETR4, MGLU3, VALE3 e ITUB4 via
brapi.dev e simuladas para os demais) e simulador de independência financeira.
