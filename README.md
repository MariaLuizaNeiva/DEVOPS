# To-Do API — DevOps: CI, Conteinerização e CD

API REST simples de gerenciamento de tarefas, construída em Python/Flask, com suíte de testes automatizados, pipeline de CI (GitHub Actions) e conteinerização (Docker).

## 1. Estrutura do repositório

```
todo-api/
├── app.py                     # API Flask
├── storage.py                 # Camada de dados (PostgreSQL / memória)
├── requirements.txt           # Dependências de runtime
├── requirements-dev.txt       # Dependências de teste
├── Dockerfile                 # Imagem multi-stage, não-root, com healthcheck
├── docker-compose.yml         # API + PostgreSQL
├── .env.example               # Modelo de variáveis (o .env real NÃO é versionado)
├── scripts/
│   ├── deploy.sh              # Deploy de uma versão via Compose
│   └── smoke_test.sh          # Validação pós-deploy (/health e /version)
├── docs/
│   └── ROLLBACK.md            # Versionamento e simulação de rollback
├── tests/
│   └── test_app.py            # Testes automatizados (pytest)
├── .github/workflows/
│   ├── ci.yml                 # CI: testes + build + validação do Compose
│   ├── cd.yml                 # CD: publica no GHCR + deploy + rollback automático
│   └── rollback.yml           # Rollback manual
├── CHANGELOG.md
└── README.md
```

## 2. Estratégia de ramificação — Trunk-Based Development

Adotamos **Trunk-Based Development**:

- `main` é o branch principal (trunk) e deve estar sempre estável/deployável.
- Desenvolvedores criam branches de vida curta a partir de `main`, ex.: `feature/criar-tarefa`, `fix/bug-status-404`.
- Commits são pequenos e integrados frequentemente via Pull Request para `main`.
- Nada de branches de longa duração (evita "merge hell").

### Convenção de commits (Conventional Commits)

```
feat: adiciona endpoint de criação de tarefa
fix: corrige validação do campo title
test: adiciona testes para exclusão de tarefa
ci: configura pipeline de build e testes
docs: atualiza README com instruções de uso
```

## 3. Regras de proteção do branch `main`

Configuração feita em **GitHub → Settings → Branches → Branch protection rules** (não é feita via código, é configuração do repositório remoto):

1. Branch: `main`
2. Marcar:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (mínimo 1 revisor — o outro integrante do grupo)
   - ✅ Require status checks to pass before merging → selecionar o job `Build & Test` do CI
   - ✅ Require branches to be up to date before merging
   - ✅ Do not allow bypassing the above settings (opcional, mas recomendado)
3. Bloquear push direto na `main` — todo código entra via PR.

## 4. Como rodar localmente (sem banco, em memória)

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python app.py
```

A API sobe em `http://localhost:5000`.

## 5. Rodando os testes automatizados

```bash
python -m pytest --cov=app --cov-report=term-missing tests/
```

## 6. Rodando com Docker Compose (API + PostgreSQL)

```bash
cp .env.example .env        # defina uma senha em POSTGRES_PASSWORD
docker compose up --build
curl http://localhost:5000/health
curl http://localhost:5000/version
```

Para encerrar: `docker compose down` (use `-v` para apagar também os dados do banco).

## 7. Endpoints da API

| Método | Rota            | Descrição                  |
|--------|-----------------|-----------------------------|
| GET    | /health         | Health check                |
| GET    | /version        | Versão em execução          |
| GET    | /tasks          | Lista todas as tarefas      |
| GET    | /tasks/<id>     | Busca uma tarefa por ID     |
| POST   | /tasks          | Cria uma nova tarefa        |
| PUT    | /tasks/<id>     | Atualiza uma tarefa         |
| DELETE | /tasks/<id>     | Remove uma tarefa           |

## 8. Pipeline de CI (GitHub Actions)

Arquivo: `.github/workflows/ci.yml`

Disparado automaticamente em:
- Push para `main`
- Abertura/atualização de Pull Request para `main`

Etapas executadas:
1. Checkout do código
2. Setup do Python 3.11
3. Instalação das dependências (build)
4. Execução da suíte de testes automatizados com relatório de cobertura
5. Build da imagem Docker, validando a conteinerização

## 9. Como publicar este repositório no GitHub

```bash
git init
git add .
git commit -m "chore: setup inicial do projeto com CI e Docker"
git branch -M main
git remote add origin <URL_DO_SEU_REPOSITORIO>
git push -u origin main
```

Depois disso, configure as regras de proteção de branch descritas na seção 3, e passe a trabalhar sempre via branches de feature + Pull Request.

---

# Fase 2 — IaC e Entrega Contínua (CD)

## 10. Pipeline de CD (`.github/workflows/cd.yml`)

Disparado por tags semânticas (`v1.0.0`):

1. **ci** — reaproveita o CI; nada é publicado se os testes falharem.
2. **publish** — build da imagem e push no **GitHub Container Registry** (`ghcr.io/<usuario>/<repo>`) com tags `1.0.0`, `1.0` e `latest`; cria a GitHub Release.
3. **deploy-staging** — deploy automático em homologação (simulado com Docker Compose no runner), *smoke test* e **rollback automático** em caso de falha.

## 11. Gestão de segredos

Nenhuma senha está no código-fonte:

- `.env` é ignorado pelo Git; só o modelo `.env.example` (sem segredo real) é versionado.
- No `docker-compose.yml`, `POSTGRES_PASSWORD` não tem valor padrão: sem o segredo, o Compose se recusa a subir.
- No CI/CD, a senha vem de **GitHub Secrets** (`secrets.POSTGRES_PASSWORD`, no environment `staging`), que o GitHub mascara nos logs.
- O login no GHCR usa o `GITHUB_TOKEN` automático, sem credencial manual.

### Configuração única no GitHub
1. *Settings → Environments → New environment* → nome `staging`.
2. Dentro do environment, *Add environment secret* → `POSTGRES_PASSWORD` = uma senha forte.
3. *Settings → Actions → General → Workflow permissions* → **Read and write permissions**.

## 12. Versionamento e rollback

Veja [`docs/ROLLBACK.md`](docs/ROLLBACK.md) para o fluxo de releases, o rollback automático/manual e o passo a passo da simulação.
