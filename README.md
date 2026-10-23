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

## Pré-requisitos

- Python 3.11 ou superior instalado.
- Um navegador (Chrome, Firefox, Edge...).

## Jeito rápido (Windows)

1. Dê dois cliques em `backend\instalar.bat` (só na primeira vez): cria o
   ambiente virtual, instala as dependências, gera o `.env` e popula o banco.
2. Dê dois cliques em `iniciar-tudo.bat`: abre a API, o front-end e o navegador.

Se preferir fazer manualmente (ou estiver no Linux/macOS), siga os passos abaixo.

## Como rodar o back-end (API)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows (PowerShell): venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env            # depois, abra o .env e ajuste se quiser
python seed.py                  # cria o banco e popula com as 3 personas
uvicorn main:app --reload
```

A API sobe em `http://localhost:8000`. A documentação interativa (Swagger) fica em
`http://localhost:8000/docs` — dá para testar todos os endpoints por lá também.

## Como rodar o front-end

Em outro terminal (deixe o back-end rodando):

```bash
cd frontend
python -m http.server 5500
```

Depois abra `http://localhost:5500/index.html` no navegador.

> Alternativa: se estiver usando o VS Code, a extensão **Live Server** também
> funciona — clique com o botão direito em `frontend/index.html` e escolha
> "Open with Live Server".

Se você mudar a porta do front-end, atualize também `FRONTEND_ORIGIN` no arquivo
`backend/.env` (usado na configuração de CORS) para o front continuar conseguindo
chamar a API.

## Credenciais de teste (as 3 personas do projeto)

| Persona | Perfil | E-mail | Senha |
|---|---|---|---|
| Juliana Souza | Iniciante | `juliana@aporta.com` | `juliana123` |
| Miguel Almeida | Intermediário | `miguel@aporta.com` | `miguel123` |
| Jéssica Mendes | Avançado | `jessica@aporta.com` | `jessica123` |

Na tela de login, clique em qualquer uma das contas de demonstração para preencher
o formulário automaticamente.

## Testes automatizados

O back-end tem 48 testes automatizados (pasta `backend/tests/`, com `pytest`).
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
├── backend/          — API em FastAPI + SQLite
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── quotes_service.py
│   ├── seed.py
│   └── routers/
└── frontend/         — HTML + CSS + JavaScript puro
    ├── index.html      (login)
    ├── painel.html
    ├── cadastro.html
    ├── simulador.html
    ├── css/
    └── js/
```

## Aviso

Este é um protótipo acadêmico e não deve ser usado com dados reais de
investimentos nem exposto publicamente na internet sem revisão adicional de
segurança.
