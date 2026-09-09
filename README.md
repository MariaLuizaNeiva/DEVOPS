# To-Do API — Marco 1: CI e Conteinerização Inicial

API REST simples de gerenciamento de tarefas, construída em Python/Flask, com suíte de testes automatizados, pipeline de CI (GitHub Actions) e conteinerização (Docker).

## 1. Estrutura do repositório

```
todo-api/
├── app.py                     # Código-fonte da aplicação
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Conteinerização da aplicação
├── .dockerignore
├── .gitignore
├── tests/
│   └── test_app.py            # Testes automatizados (pytest)
├── .github/
│   └── workflows/
│       └── ci.yml             # Pipeline de CI (build + testes)
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

## 4. Como rodar localmente

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

A API sobe em `http://localhost:5000`.

## 5. Rodando os testes automatizados

```bash
pytest --cov=app --cov-report=term-missing tests/
```

## 6. Rodando com Docker (conteinerização inicial)

```bash
docker build -t todo-api .
docker run -p 5000:5000 todo-api
```

## 7. Endpoints da API

| Método | Rota            | Descrição                  |
|--------|-----------------|-----------------------------|
| GET    | /health         | Health check                |
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

Isso é um teste.
