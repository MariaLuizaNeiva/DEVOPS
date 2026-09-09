"""
Testes automatizados (unitários/integração) da API de Tarefas.
Executados automaticamente pelo pipeline de CI a cada push/PR.
"""
import pytest
from app import app, tasks


@pytest.fixture(autouse=True)
def reset_state():
    """Garante que cada teste começa com o estado limpo."""
    tasks.clear()
    yield
    tasks.clear()


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Estudar CI/CD"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Estudar CI/CD"
    assert data["done"] is False
    assert data["id"] == 1


def test_create_task_without_title_fails(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_task_by_id(client):
    created = client.post("/tasks", json={"title": "Ler artigo"}).get_json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Ler artigo"


def test_get_nonexistent_task_returns_404(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_update_task(client):
    created = client.post("/tasks", json={"title": "Tarefa original"}).get_json()
    response = client.put(
        f"/tasks/{created['id']}", json={"title": "Tarefa atualizada", "done": True}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Tarefa atualizada"
    assert data["done"] is True


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Tarefa temporária"}).get_json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204

    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 404


def test_list_tasks_after_creation(client):
    client.post("/tasks", json={"title": "Tarefa 1"})
    client.post("/tasks", json={"title": "Tarefa 2"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.get_json()) == 2
