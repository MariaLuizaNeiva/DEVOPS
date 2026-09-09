"""
API de Gerenciamento de Tarefas (To-Do List)
Aplicação simples em Flask com operações CRUD em memória.
"""
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# "Banco de dados" em memória (apenas para fins didáticos)
tasks = []
next_id = 1


def find_task(task_id):
    return next((t for t in tasks if t["id"] == task_id), None)


@app.route("/health", methods=["GET"])
def health():
    """Endpoint simples para health check (útil em containers)."""
    return jsonify({"status": "ok"}), 200


@app.route("/tasks", methods=["GET"])
def list_tasks():
    return jsonify(tasks), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = find_task(task_id)
    if task is None:
        abort(404, description="Tarefa não encontrada")
    return jsonify(task), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    global next_id
    data = request.get_json(silent=True)

    if not data or "title" not in data or not str(data["title"]).strip():
        abort(400, description="O campo 'title' é obrigatório")

    task = {
        "id": next_id,
        "title": data["title"],
        "done": bool(data.get("done", False)),
    }
    tasks.append(task)
    next_id += 1
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = find_task(task_id)
    if task is None:
        abort(404, description="Tarefa não encontrada")

    data = request.get_json(silent=True) or {}
    if "title" in data:
        task["title"] = data["title"]
    if "done" in data:
        task["done"] = bool(data["done"])

    return jsonify(task), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = find_task(task_id)
    if task is None:
        abort(404, description="Tarefa não encontrada")

    tasks.remove(task)
    return "", 204


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
