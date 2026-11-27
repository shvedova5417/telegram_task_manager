
"""Настройки Telegram-бота."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Корневая папка проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Загружаем переменные из .env
load_dotenv(BASE_DIR / ".env")

# Токен Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Путь к базе данных
DATABASE_PATH = BASE_DIR / "tasks.db"


def get_bot_token() -> str:
    """Возвращает токен бота или сообщает об отсутствии настройки."""
    if not BOT_TOKEN:
        raise ValueError(
            "Не найден BOT_TOKEN. Создайте файл .env "
            "и добавьте в него токен Telegram-бота."
        )

    return BOT_TOKEN
