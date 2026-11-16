import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.db")

_conn = None


def get_conn():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH)
        _conn.row_factory = sqlite3.Row
    return _conn


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            priority TEXT DEFAULT 'Обычный'
        )
        """
    )
    conn.commit()


def load_tasks():
    """Вернуть все задачи в порядке добавления."""
    conn = get_conn()
    return conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()


def add_task(text, priority):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO tasks (text, priority) VALUES (?, ?)",
        (text, priority),
    )
    conn.commit()
    return cur.lastrowid


def delete_task(task_id):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()


def update_task(task_id, text, priority):
    conn = get_conn()
    conn.execute(
        "UPDATE tasks SET text = ?, priority = ? WHERE id = ?",
        (text, priority, task_id),
    )
    conn.commit()