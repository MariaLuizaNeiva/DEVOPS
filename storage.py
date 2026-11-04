"""
Camada de armazenamento da API.

- MemoryStorage: usada quando DATABASE_URL não está definida (testes / execução simples).
- PostgresStorage: usada quando DATABASE_URL está definida (Docker Compose / deploy).
"""
import os
import time
from contextlib import contextmanager


class MemoryStorage:
    name = "memory"

    def __init__(self):
        self.clear()

    def clear(self):
        self._tasks = []
        self._next_id = 1

    def ping(self):
        return True

    def list(self):
        return [dict(t) for t in self._tasks]

    def get(self, task_id):
        task = next((t for t in self._tasks if t["id"] == task_id), None)
        return dict(task) if task else None

    def create(self, title, done=False):
        task = {"id": self._next_id, "title": title, "done": bool(done)}
        self._tasks.append(task)
        self._next_id += 1
        return dict(task)

    def update(self, task_id, title=None, done=None):
        task = next((t for t in self._tasks if t["id"] == task_id), None)
        if task is None:
            return None
        if title is not None:
            task["title"] = title
        if done is not None:
            task["done"] = bool(done)
        return dict(task)

    def delete(self, task_id):
        task = next((t for t in self._tasks if t["id"] == task_id), None)
        if task is None:
            return False
        self._tasks.remove(task)
        return True


class PostgresStorage:
    name = "postgres"

    def __init__(self, dsn, retries=15, delay=2):
        import psycopg2  # importado aqui para não ser exigido quando se usa MemoryStorage

        self._psycopg2 = psycopg2
        self.dsn = dsn
        last_error = None
        for _ in range(retries):
            try:
                self._init_schema()
                return
            except psycopg2.OperationalError as exc:  # banco ainda subindo
                last_error = exc
                time.sleep(delay)
        raise last_error

    @contextmanager
    def _cursor(self):
        from psycopg2.extras import RealDictCursor

        conn = self._psycopg2.connect(self.dsn)
        try:
            with conn:  # commit/rollback automático
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    yield cur
        finally:
            conn.close()

    def _init_schema(self):
        with self._cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id    SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    done  BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )

    def clear(self):
        with self._cursor() as cur:
            cur.execute("TRUNCATE tasks RESTART IDENTITY")

    def ping(self):
        try:
            with self._cursor() as cur:
                cur.execute("SELECT 1")
            return True
        except Exception:
            return False

    def list(self):
        with self._cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
            return [dict(r) for r in cur.fetchall()]

    def get(self, task_id):
        with self._cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def create(self, title, done=False):
        with self._cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
                (title, bool(done)),
            )
            return dict(cur.fetchone())

    def update(self, task_id, title=None, done=None):
        current = self.get(task_id)
        if current is None:
            return None
        new_title = current["title"] if title is None else title
        new_done = current["done"] if done is None else bool(done)
        with self._cursor() as cur:
            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
                (new_title, new_done, task_id),
            )
            return dict(cur.fetchone())

    def delete(self, task_id):
        with self._cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            return cur.rowcount > 0


def create_storage():
    dsn = os.environ.get("DATABASE_URL")
    if dsn:
        return PostgresStorage(dsn)
    return MemoryStorage()
