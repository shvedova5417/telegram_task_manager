
"""Сервисный слой для работы с задачами."""

from html import escape

from database.db_manager import (
    add_task,
    get_all_tasks,
    update_task_status,
    update_task_text,
    delete_task,
)

# Максимальное количество задач на одной странице
TASKS_PER_PAGE = 10

# Названия статусов для отображения пользователю
STATUS_LABELS = {
    "new": "🆕 Новая",
    "in_progress": "⏳ В работе",
    "done": "✅ Выполнена",
}


def create_task(text: str, user: str) -> int:
    """Создаёт новую задачу."""
    return add_task(text, user)


def get_tasks_page(page: int = 1) -> tuple[list[dict], int]:
    """Возвращает страницу задач и общее количество страниц."""
    if page < 1:
        page = 1

    all_tasks = get_all_tasks()
    total_pages = max(
        1,
        (len(all_tasks) + TASKS_PER_PAGE - 1) // TASKS_PER_PAGE
    )

    page = min(page, total_pages)
    start = (page - 1) * TASKS_PER_PAGE
    end = start + TASKS_PER_PAGE

    return all_tasks[start:end], total_pages


def change_task_status(task_id: int, status: str) -> bool:
    """Изменяет статус задачи."""
    return update_task_status(task_id, status)


def edit_task(task_id: int, text: str) -> bool:
    """Редактирует текст задачи."""
    return update_task_text(task_id, text)


def remove_task(task_id: int) -> bool:
    """Удаляет задачу."""
    return delete_task(task_id)


def format_tasks(tasks: list[dict], page: int, total_pages: int) -> str:
    """Формирует безопасное HTML-представление списка задач."""
    if not tasks:
        return "📭 Список задач пока пуст."

    lines = [
        f"<b>📋 Список задач</b>",
        f"Страница {page} из {total_pages}",
        ""
    ]

    for task in tasks:
        task_id = task["id"]
        task_text = escape(task["text"])
        author = escape(task["user"])
        status = STATUS_LABELS.get(task["status"], "❔ Неизвестно")
        created_at = escape(task["created_at"])

        lines.append(
            f"<b>#{task_id}</b> {status}\n"
            f"📝 {task_text}\n"
            f"👤 Автор: {author}\n"
            f"📅 Создана: {created_at}\n"
        )

    return "\n".join(lines)
