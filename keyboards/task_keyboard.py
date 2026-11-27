
"""Inline-клавиатуры для управления задачами."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_task_keyboard(task_id: int, status: str) -> InlineKeyboardMarkup:
    """Создаёт кнопки управления конкретной задачей."""
    buttons = []

    if status == "new":
        buttons.append([
            InlineKeyboardButton(
                text="⏳ В работу",
                callback_data=f"task_work:{task_id}"
            ),
            InlineKeyboardButton(
                text="✅ Выполнена",
                callback_data=f"task_done:{task_id}"
            )
        ])

    elif status == "in_progress":
        buttons.append([
            InlineKeyboardButton(
                text="✅ Выполнена",
                callback_data=f"task_done:{task_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="✏️ Изменить",
            callback_data=f"task_edit:{task_id}"
        ),
        InlineKeyboardButton(
            text="🗑 Удалить",
            callback_data=f"task_delete:{task_id}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_tasks_pagination_keyboard(
    page: int,
    total_pages: int
) -> InlineKeyboardMarkup | None:
    """Создаёт кнопки перехода между страницами."""
    buttons = []

    if page > 1:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"tasks_page:{page - 1}"
            )
        )

    if page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"tasks_page:{page + 1}"
            )
        )

    if not buttons:
        return None

    return InlineKeyboardMarkup(inline_keyboard=[buttons])
