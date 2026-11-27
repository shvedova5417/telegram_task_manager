

"""Обработчики команд и сообщений Telegram-бота."""

from html import escape

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from keyboards.main_keyboard import (
    get_main_keyboard,
    get_cancel_keyboard,
)
from keyboards.task_keyboard import (
    get_task_keyboard,
    get_tasks_pagination_keyboard,
)
from services.task_service import (
    create_task,
    get_tasks_page,
    format_tasks,
)
from database.db_manager import get_all_tasks

router = Router()


class AddTaskStates(StatesGroup):
    """Состояния процесса добавления задачи."""
    waiting_for_task = State()


async def send_tasks_page(message: Message, page: int = 1):
    """Отправляет страницу задач с кнопками управления."""
    tasks, total_pages = get_tasks_page(page)

    if not tasks:
        await message.answer(
            "📭 Список задач пока пуст.",
            reply_markup=get_main_keyboard()
        )
        return

    for task in tasks:
        await message.answer(
            format_tasks([task], 1, 1),
            parse_mode="HTML",
            reply_markup=get_task_keyboard(
                task["id"],
                task["status"]
            )
        )

    pagination = get_tasks_pagination_keyboard(page, total_pages)

    if pagination:
        await message.answer(
            f"Страница {page} из {total_pages}",
            reply_markup=pagination
        )


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Приветствие и главное меню."""
    name = escape(message.from_user.first_name or "пользователь")

    await message.answer(
        f"👋 Привет, {name}!\n\n"
        "Я помогу управлять задачами.\n\n"
        "Доступные команды:\n"
        "/add — добавить задачу\n"
        "/list — список задач\n"
        "/stats — статистика\n"
        "/help — помощь",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message):
    """Справочная информация."""
    await message.answer(
        "<b>Инструкция по работе с ботом</b>\n\n"
        "➕ Добавить задачу — создать новую задачу.\n"
        "📋 Список задач — просмотреть задачи.\n"
        "📊 Статистика — посмотреть состояние задач.\n\n"
        "Команды:\n"
        "/add — добавить задачу\n"
        "/list — показать список\n"
        "/stats — статистика\n"
        "/cancel — отменить действие",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("add"))
@router.message(F.text == "➕ Добавить задачу")
async def cmd_add(message: Message, state: FSMContext):
    """Начинает процесс добавления задачи."""
    await state.set_state(AddTaskStates.waiting_for_task)

    await message.answer(
        "✍️ Напиши текст новой задачи.",
        reply_markup=get_cancel_keyboard()
    )


@router.message(
    AddTaskStates.waiting_for_task,
    Command("cancel")
)
@router.message(
    AddTaskStates.waiting_for_task,
    F.text == "❌ Отмена"
)
async def cancel_add_task(message: Message, state: FSMContext):
    """Отменяет добавление задачи."""
    await state.clear()

    await message.answer(
        "❌ Добавление отменено.",
        reply_markup=get_main_keyboard()
    )


@router.message(AddTaskStates.waiting_for_task)
async def process_add_task(message: Message, state: FSMContext):
    """Проверяет и сохраняет новую задачу."""
    if not message.text:
        await message.answer(
            "⚠️ Нужно отправить именно текстовое сообщение. "
            "Попробуй ещё раз или нажми «❌ Отмена»."
        )
        return

    task_text = message.text.strip()

    if not task_text:
        await message.answer("⚠️ Текст задачи не может быть пустым.")
        return

    if len(task_text) > 1000:
        await message.answer(
            "⚠️ Слишком длинная задача. Максимум — 1000 символов."
        )
        return

    user_name = (
        message.from_user.first_name
        or message.from_user.username
        or "Аноним"
    )

    try:
        task_id = create_task(task_text, user_name)
    except ValueError as error:
        await message.answer(f"⚠️ {error}")
        return

    await state.clear()

    await message.answer(
        f"✅ Задача #{task_id} успешно добавлена!",
        reply_markup=get_main_keyboard()
    )


@router.message(Command("list"))
@router.message(F.text == "📋 Список задач")
async def cmd_list(message: Message):
    """Показывает первую страницу задач."""
    await send_tasks_page(message, 1)


@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика")
async def cmd_stats(message: Message):
    """Показывает статистику задач."""
    tasks = get_all_tasks()

    total = len(tasks)
    new = sum(task["status"] == "new" for task in tasks)
    in_progress = sum(
        task["status"] == "in_progress" for task in tasks
    )
    done = sum(task["status"] == "done" for task in tasks)

    await message.answer(
        "<b>📊 Статистика задач</b>\n\n"
        f"Всего: {total}\n"
        f"🆕 Новые: {new}\n"
        f"⏳ В работе: {in_progress}\n"
        f"✅ Выполненные: {done}",
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
