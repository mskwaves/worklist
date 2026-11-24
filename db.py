import sqlite3
import os
from datetime import date

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
            text_lower TEXT,
            priority TEXT DEFAULT 'Обычный'
        )
        """
    )
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()]
    if "text_lower" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN text_lower TEXT")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            priority TEXT DEFAULT 'Обычный',
            archived_at TEXT NOT NULL
        )
        """
    )
    rows = conn.execute("SELECT id, text FROM tasks WHERE text_lower IS NULL").fetchall()
    for row in rows:
        conn.execute(
            "UPDATE tasks SET text_lower = ? WHERE id = ?",
            (row["text"].lower(), row["id"]),
        )
    conn.commit()


def load_tasks():
    """Вернуть все задачи в порядке добавления."""
    conn = get_conn()
    return conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()


def search_tasks(query):
    """Вернуть задачи, в тексте которых встречается подстрока query (без учёта регистра)."""
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM tasks WHERE text_lower LIKE ? ORDER BY id",
        (f"%{query.lower()}%",),
    ).fetchall()


def add_task(text, priority):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO tasks (text, text_lower, priority) VALUES (?, ?, ?)",
        (text, text.lower(), priority),
    )
    conn.commit()
    return cur.lastrowid


def delete_task(task_id):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()


def archive_task(task_id):
    """Перенести задачу из tasks в archive, вернуть True при успехе."""
    conn = get_conn()
    row = conn.execute(
        "SELECT text, priority FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if row is None:
        return False
    conn.execute(
        "INSERT INTO archive (text, priority, archived_at) VALUES (?, ?, ?)",
        (row["text"], row["priority"], date.today().isoformat()),
    )
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return True


def load_archive():
    """Вернуть выполненные задачи, сначала свежие."""
    conn = get_conn()
    return conn.execute("SELECT * FROM archive ORDER BY id DESC").fetchall()


def update_task(task_id, text, priority):
    conn = get_conn()
    conn.execute(
        "UPDATE tasks SET text = ?, text_lower = ?, priority = ? WHERE id = ?",
        (text, text.lower(), priority, task_id),
    )
    conn.commit()