# Notas de atualização

Registro das mudanças do protótipo Aporta.

---

## Versão 0.2.2 — 21/11/2026

Correções de bugs encontrados na revisão do código, botão "Sair" e proteção
contra telas antigas em cache.

### 🆕 Novidades

- **Botão "Sair"** na barra superior das telas Painel, Ativos e Simulador. O círculo
  com as iniciais agora só identifica o usuário (antes ele mesmo era o botão de sair).
- Adicionado `.gitignore` na raiz do projeto (`.DS_Store`, `.vscode/`, `__pycache__/`,
  `.env`, `venv/`, `aporta.db`).

### 🐛 Correções

- **Login:** a mensagem "E-mail ou senha inválidos" voltou a aparecer. Antes, a página
  recarregava e a mensagem sumia.
- **Erros de validação** da API aparecem como texto legível, em vez de "[object Object]".
- **Cotações:** passou a existir uma cotação por código, com o preço médio ponderado dos
  lotes. Antes, dois lotes do mesmo ticker podiam ser avaliados por preços diferentes.
- **brapi.dev fora do ar:** após uma falha, a API espera 60 s antes de tentar de novo,
  evitando telas lentas (até 20 s por requisição).
- **Tela Ativos presa em "Carregando...":** a barra superior não derruba mais o resto da
  página se faltar algum elemento (isso acontecia ao misturar arquivos de versões diferentes).
- O painel e o simulador encontram a cotação mesmo se o código do ativo estiver em
  minúsculas no banco.

### ⚙️ Configuração

- **CORS:** `FRONTEND_ORIGIN` aceita várias origens separadas por vírgula. O padrão
  libera `http://localhost:5500` e `http://127.0.0.1:5500`. Quem já tem um `backend/.env`
  com uma origem só precisa editá-lo para liberar a segunda.
- **Cache:** o servidor envia o front-end com `Cache-Control: no-cache`, e os arquivos
  CSS/JS levam `?v=0.2.1` nos links. Assim o navegador não mostra telas antigas depois
  de atualizar o projeto. (Se o front for servido por `python -m http.server`, só o
  `?v=` vale; troque o número a cada versão.)

### 🧪 Testes

- O back-end passou de 48 para **52 testes** (novos: lotes do mesmo código, espera após
  falha da brapi.dev, CORS com as duas origens e front-end sem cache).

---

## Versão 0.2.1 — 21/11/2026

Facilita a execução do protótipo em qualquer sistema e corrige uma falha de
segurança no login.

### 🔒 Segurança

- **Corrigido o vazamento de usuários cadastrados pelo tempo de resposta do
  login.** Com e-mail inexistente, a API respondia em ~0,003 s; com e-mail
  existente, em ~0,226 s (o bcrypt só rodava quando o usuário existia). Dava para
  descobrir quais e-mails estavam cadastrados cronometrando as respostas. Agora,
  se o e-mail não existe, a senha é verificada contra um hash falso
  (`DUMMY_PASSWORD_HASH`, em `auth.py`), e os dois casos levam o mesmo tempo.
- **A chave `JWT_SECRET_KEY` agora é gerada aleatoriamente.** Antes, o
  `instalar.bat` copiava o `.env.example` com a chave de exemplo (pública), e todas
  as instalações acabavam usando a mesma. O novo `backend/gerar_env.py` cria o
  `.env` com uma chave aleatória e não sobrescreve um `.env` existente.

### ⚙️ Instalação e uso

- **O back-end agora serve o front-end** (`StaticFiles`, em `main.py`). Tudo sobe
  junto em `http://localhost:8000`, sem segundo servidor e sem depender de CORS. O
  `api.js` usa caminho relativo na porta 8000 e mantém o endereço antigo
  (`localhost:8000` com front na 5500) como alternativa.
- **Novo `run.py` na raiz:** um comando (`python run.py`) cria o `.env` e o banco
  com as 3 personas, sobe a API e o front-end e abre o navegador. Funciona em
  Windows, macOS e Linux.
- **Chart.js incluído no projeto** (`frontend/js/chart.umd.min.js`), em vez de
  carregado de CDN. Os gráficos do painel e do simulador funcionam sem internet.
- **Adicionado o `favicon.svg`**, que remove o aviso `404 /favicon.ico` do log.
- README reescrito: passo a passo com ambiente virtual (necessário no macOS e em
  Linux recentes, que bloqueiam a instalação global de pacotes), remoção da seção
  do front-end em servidor separado e aviso de que abrir o `index.html` por duplo
  clique (`file://`) não funciona.

### 📌 Pendências conhecidas

- O `iniciar-tudo.bat` ainda abre um servidor separado do front-end na porta 5500;
  funciona, mas ficou redundante.
- Continuam as pendências da versão 0.2.0 (valores em `Float`, sem cadastro de
  usuário nem edição de ativo, cotação simulada que muda a cada recarregamento).

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
