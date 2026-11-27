
"""Обработчики inline-кнопок управления задачами."""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db_manager import (
    get_task_by_id,
    update_task_status,
    update_task_text,
    delete_task,
)
from keyboards.main_keyboard import get_main_keyboard
from keyboards.task_keyboard import (
    get_task_keyboard,
    get_tasks_pagination_keyboard,
)
from services.task_service import get_tasks_page, format_tasks

router = Router()


class EditTaskStates(StatesGroup):
    """Состояние редактирования задачи."""
    waiting_for_new_text = State()


@router.callback_query(F.data.startswith("task_work:"))
async def mark_in_progress(callback: CallbackQuery):
    """Переводит задачу в статус «В работе»."""
    task_id = int(callback.data.split(":")[1])

    if not update_task_status(task_id, "in_progress"):
        await callback.answer("Задача не найдена.", show_alert=True)
        return

    task = get_task_by_id(task_id)

    await callback.message.edit_reply_markup(
        reply_markup=get_task_keyboard(task_id, task["status"])
    )
    await callback.answer("Задача переведена в работу.")


@router.callback_query(F.data.startswith("task_done:"))
async def mark_done(callback: CallbackQuery):
    """Отмечает задачу выполненной."""
    task_id = int(callback.data.split(":")[1])

    if not update_task_status(task_id, "done"):
        await callback.answer("Задача не найдена.", show_alert=True)
        return

    task = get_task_by_id(task_id)

    await callback.message.edit_reply_markup(
        reply_markup=get_task_keyboard(task_id, task["status"])
    )
    await callback.answer("Задача выполнена!")


@router.callback_query(F.data.startswith("task_edit:"))
async def start_edit_task(
    callback: CallbackQuery,
    state: FSMContext
):
    """Запускает редактирование задачи."""
    task_id = int(callback.data.split(":")[1])
    task = get_task_by_id(task_id)

    if not task:
        await callback.answer("Задача не найдена.", show_alert=True)
        return

    await state.update_data(task_id=task_id)
    await state.set_state(EditTaskStates.waiting_for_new_text)

    await callback.message.answer(
        f"✏️ Введите новый текст для задачи #{task_id}.\n"
        "Для отмены отправьте /cancel."
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_delete:"))
async def confirm_delete_task(callback: CallbackQuery):
    """Показывает подтверждение удаления."""
    task_id = int(callback.data.split(":")[1])
    task = get_task_by_id(task_id)

    if not task:
        await callback.answer("Задача не найдена.", show_alert=True)
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="Да, удалить",
                callback_data=f"task_confirm_delete:{task_id}"
            ),
            InlineKeyboardButton(
                text="Отмена",
                callback_data=f"task_cancel_delete:{task_id}"
            )
        ]]
    )

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("task_confirm_delete:"))
async def delete_task_callback(callback: CallbackQuery):
    """Удаляет задачу после подтверждения."""
    task_id = int(callback.data.split(":")[1])

    if not delete_task(task_id):
        await callback.answer("Задача не найдена.", show_alert=True)
        return

    await callback.message.edit_text("🗑 Задача удалена.")
    await callback.answer("Удаление выполнено.")


@router.callback_query(F.data.startswith("task_cancel_delete:"))
async def cancel_delete_task(callback: CallbackQuery):
    """Отменяет удаление задачи."""
    task_id = int(callback.data.split(":")[1])
    task = get_task_by_id(task_id)

    if task:
        await callback.message.edit_reply_markup(
            reply_markup=get_task_keyboard(task_id, task["status"])
        )
    else:
        await callback.message.edit_reply_markup(reply_markup=None)

    await callback.answer("Удаление отменено.")


@router.callback_query(F.data.startswith("tasks_page:"))
async def show_tasks_page(callback: CallbackQuery):
    """Показывает выбранную страницу задач."""
    page = int(callback.data.split(":")[1])
    tasks, total_pages = get_tasks_page(page)

    for task in tasks:
        await callback.message.answer(
            format_tasks([task], 1, 1),
            parse_mode="HTML",
            reply_markup=get_task_keyboard(
                task["id"],
                task["status"]
            )
        )

    pagination = get_tasks_pagination_keyboard(page, total_pages)

    if pagination:
        await callback.message.answer(
            f"Страница {page} из {total_pages}",
            reply_markup=pagination
        )

    await callback.answer()


@router.message(
    EditTaskStates.waiting_for_new_text,
    Command("cancel")
)
async def cancel_edit_task(message: Message, state: FSMContext):
    """Отменяет редактирование задачи."""
    await state.clear()
    await message.answer(
        "Редактирование отменено.",
        reply_markup=get_main_keyboard()
    )


@router.message(EditTaskStates.waiting_for_new_text)
async def process_edit_task(message: Message, state: FSMContext):
    """Сохраняет новый текст задачи."""
    if not message.text or not message.text.strip():
        await message.answer("⚠️ Отправьте непустой текст.")
        return

    new_text = message.text.strip()

    if len(new_text) > 1000:
        await message.answer("⚠️ Максимальная длина — 1000 символов.")
        return

    data = await state.get_data()
    task_id = data.get("task_id")

    if not task_id or not update_task_text(task_id, new_text):
        await state.clear()
        await message.answer("Задача не найдена.")
        return

    await state.clear()

    await message.answer(
        f"✅ Текст задачи #{task_id} изменён.",
        reply_markup=get_main_keyboard()
    )
