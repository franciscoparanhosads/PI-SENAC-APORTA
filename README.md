# Aporta — Plataforma de Gestão e Análise de Investimentos Pessoais

**Protótipo acadêmico** — Projeto Integrador, Centro Universitário Senac (2026).

## O que é

Uma plataforma web que centraliza investimentos pessoais em diferentes classes de
ativos (Renda Fixa, FIIs, Ações e Criptomoedas), com um painel de alocação
patrimonial e um simulador de independência financeira.

Este projeto **apenas informa e simula** — não recomenda a compra ou venda de
nenhum ativo (restrição da CVM para plataformas que não são consultorias
registradas). Todos os dados exibidos são fictícios, criados apenas para fins de
demonstração acadêmica.

As mudanças de cada versão estão em [CHANGELOG.md](CHANGELOG.md).

## Pré-requisitos

- Python 3.11 ou superior instalado.
- Um navegador (Chrome, Firefox, Edge...).

## Como rodar

O back-end (API) também serve o front-end, então tudo sobe junto em
`http://localhost:8000`. Não é preciso um segundo servidor, e o Chart.js já vem na
pasta do projeto (`frontend/js/`), então os gráficos funcionam sem internet.

### Jeito mais rápido (macOS, Linux e Windows)

Na pasta raiz do projeto (a que contém o `run.py`), **na primeira vez**:

```bash
python3 -m venv backend/venv
source backend/venv/bin/activate        # Windows (PowerShell): backend\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python run.py
```

Nas próximas vezes, basta ativar o ambiente virtual e rodar:

```bash
source backend/venv/bin/activate        # Windows (PowerShell): backend\venv\Scripts\Activate.ps1
python run.py
```

O `run.py` cria o `.env` (com uma chave secreta aleatória) e o banco com as 3
personas se ainda não existirem, sobe a API e o front-end e abre o navegador.
Para parar, aperte `Ctrl + C` no terminal.

> O ambiente virtual (`venv`) é necessário no macOS e em Linux recentes: o sistema
> bloqueia a instalação global de pacotes com o erro `externally-managed-environment`.

### Jeito rápido (Windows, com dois cliques)

1. Dê dois cliques em `backend\instalar.bat` (só na primeira vez): cria o
   ambiente virtual, instala as dependências, gera o `.env` e popula o banco.
2. Dê dois cliques em `iniciar-tudo.bat`: inicia o sistema e abre o navegador.

### Manualmente (com recarga automática)

Útil durante o desenvolvimento: o servidor reinicia sozinho quando você edita o
código. A partir da pasta raiz:

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows (PowerShell): venv\Scripts\Activate.ps1
pip install -r requirements.txt
python gerar_env.py             # cria o .env com uma chave secreta aleatória
python seed.py                  # cria o banco e popula com as 3 personas
uvicorn main:app --reload
```

Depois abra `http://localhost:8000`. A documentação interativa (Swagger) fica em
`http://localhost:8000/docs` — dá para testar todos os endpoints por lá também.

## Compatibilidade (Windows, macOS e Linux)

O projeto foi feito para rodar igual em qualquer sistema: usa só Python (3.11 ou
superior) e caminhos independentes de sistema operacional. Os testes automáticos
rodam em Windows, macOS e Linux a cada envio ao GitHub (ver
`.github/workflows/testes.yml`).

Problemas comuns:

- **`python` não encontrado (macOS/Linux):** use `python3` no lugar de `python`.
- **PowerShell bloqueia o `Activate.ps1` (Windows):** rode uma vez
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e tente de novo.
- **`externally-managed-environment` ao instalar pacotes:** crie e ative o ambiente
  virtual (`venv`), como mostrado acima.
- **Cotações aparecem como "simulado":** a consulta à brapi.dev falhou (sem
  internet, por exemplo). O sistema continua funcionando; o motivo aparece como
  aviso no terminal do back-end.

## Credenciais de teste (as 3 personas do projeto)

| Persona | Perfil | E-mail | Senha |
|---|---|---|---|
| Juliana Souza | Iniciante | `juliana@aporta.com` | `juliana123` |
| Miguel Almeida | Intermediário | `miguel@aporta.com` | `miguel123` |
| Jéssica Mendes | Avançado | `jessica@aporta.com` | `jessica123` |

Na tela de login, clique em qualquer uma das contas de demonstração para preencher
o formulário automaticamente.

## Testes automatizados

O back-end tem 55 testes automatizados (pasta `backend/tests/`, com `pytest`).
No Windows, basta dar dois cliques em `backend\rodar-testes.bat`. Ou, no terminal,
com o ambiente virtual ativado:

```bash
cd backend
python -m pytest
```

Os testes usam um banco temporário (o `aporta.db` não é alterado) e não acessam a
internet (a brapi.dev é simulada). O que eles verificam:

- **Autenticação** (`test_auth.py`): login certo/errado, mesma mensagem para senha
  errada e e-mail inexistente, senha salva só como hash bcrypt, e bloqueio das
  rotas sem token, com token inválido, expirado ou assinado com outra chave.
- **Ativos** (`test_assets.py`): criar, listar e remover; rejeição de dados
  inválidos; cada usuário só vê os próprios ativos; **um usuário não consegue
  apagar o ativo de outro**, mesmo sabendo o id.
- **Simulador** (`test_simulator.py`): o resultado bate com a fórmula de juros
  compostos; casos de meta já atingida, meta inalcançável e valores inválidos.
- **Cotações** (`test_quotes.py`): cotação real para os 4 tickers, cache de 60s,
  valor reserva marcado como "simulado" quando a brapi.dev cai, e variação da
  cotação simulada dentro de ±1,5%.

## Sobre as cotações

- **PETR4, MGLU3, VALE3 e ITUB4** têm cotação real, consultada pelo back-end
  diretamente na [brapi.dev](https://brapi.dev) (não precisa de conta nem token
  para esses 4 tickers).
- **Qualquer outro ativo** (demais ações, FIIs, renda fixa, cripto) recebe uma
  cotação **simulada**, com pequena variação aleatória a cada consulta — a
  interface indica isso com a etiqueta "simulado" ao lado do ativo.
- Se a brapi.dev estiver fora do ar, o back-end usa um valor de fallback
  automaticamente, para a tela nunca quebrar.

## Estrutura do projeto

```
projeto-integrador/
├── README.md
├── CHANGELOG.md      — notas de atualização
├── run.py            — sobe tudo com um comando (qualquer sistema)
├── iniciar-tudo.bat
├── backend/          — API em FastAPI + SQLite (também serve o front-end)
│   ├── instalar.bat
│   ├── rodar-testes.bat
│   ├── gerar_env.py    — cria o .env com chave secreta aleatória
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── quotes_service.py
│   ├── seed.py
│   ├── routers/
│   └── tests/        — testes automatizados (pytest)
└── frontend/         — HTML + CSS + JavaScript puro
    ├── index.html      (login)
    ├── painel.html
    ├── cadastro.html
    ├── simulador.html
    ├── css/
    └── js/             (inclui o Chart.js local)
```

## Aviso

Este é um protótipo acadêmico e não deve ser usado com dados reais de
investimentos nem exposto publicamente na internet sem revisão adicional de
segurança.