"""
API de Gerenciamento de Tarefas (To-Do List)
Flask + armazenamento em PostgreSQL (ou memória quando DATABASE_URL não está definida).
"""
import os

from flask import Flask, jsonify, request, abort

from storage import create_storage

app = Flask(__name__)

# Versão da aplicação: injetada na imagem Docker no build (ARG APP_VERSION)
APP_VERSION = os.environ.get("APP_VERSION", "dev")

storage = create_storage()


@app.route("/health", methods=["GET"])
def health():
    """Health check: confirma que a aplicação e o armazenamento respondem."""
    if not storage.ping():
        return jsonify({"status": "unavailable"}), 503
    return jsonify({"status": "ok"}), 200


@app.route("/version", methods=["GET"])
def version():
    """Retorna a versão em execução (usada para evidenciar deploy e rollback)."""
    return jsonify({"version": APP_VERSION, "storage": storage.name}), 200


@app.route("/tasks", methods=["GET"])
def list_tasks():
    return jsonify(storage.list()), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = storage.get(task_id)
    if task is None:
        abort(404, description="Tarefa não encontrada")
    return jsonify(task), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)

    if not data or "title" not in data or not str(data["title"]).strip():
        abort(400, description="O campo 'title' é obrigatório")

    task = storage.create(data["title"], data.get("done", False))
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    task = storage.update(task_id, data.get("title"), data.get("done"))
    if task is None:
        abort(404, description="Tarefa não encontrada")
    return jsonify(task), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    if not storage.delete(task_id):
        abort(404, description="Tarefa não encontrada")
    return "", 204


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e.description)}), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
