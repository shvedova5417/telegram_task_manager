
"""Модуль управления базой данных SQLite."""

import sqlite3
from datetime import datetime

from config.settings import DATABASE_PATH


def get_connection():
    """Создаёт подключение к базе данных."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Создаёт таблицу задач, если она ещё не существует."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                user TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'new'
                    CHECK(status IN ('new', 'in_progress', 'done')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        connection.commit()


def add_task(text: str, user: str) -> int:
    """Добавляет новую задачу и возвращает её ID."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Текст задачи не может быть пустым.")

    if not isinstance(user, str) or not user.strip():
        raise ValueError("Необходимо указать автора задачи.")

    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (text, user, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (text.strip(), user.strip(), now, now)
        )
        return cursor.lastrowid


def get_all_tasks():
    """Возвращает все задачи от новых к старым."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            SELECT id, text, user, status, created_at, updated_at
            FROM tasks
            ORDER BY created_at DESC, id DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]


def get_task_by_id(task_id: int):
    """Возвращает задачу по её ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def update_task_status(task_id: int, status: str) -> bool:
    """Изменяет статус задачи."""
    allowed_statuses = {"new", "in_progress", "done"}

    if status not in allowed_statuses:
        raise ValueError("Недопустимый статус задачи.")

    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET status = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, now, task_id)
        )
        return cursor.rowcount > 0


def update_task_text(task_id: int, text: str) -> bool:
    """Изменяет текст задачи."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Текст задачи не может быть пустым.")

    now = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET text = ?, updated_at = ?
            WHERE id = ?
            """,
            (text.strip(), now, task_id)
        )
        return cursor.rowcount > 0


def delete_task(task_id: int) -> bool:
    """Удаляет задачу по её ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )
        return cursor.rowcount > 0

