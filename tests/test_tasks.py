
"""Тесты функций управления задачами."""

import pytest

import database.db_manager as db
from services.task_service import (
    create_task,
    get_tasks_page,
    change_task_status,
    edit_task,
    remove_task,
)


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """Создаёт отдельную временную базу данных для тестов."""
    test_db_path = tmp_path / "test_tasks.db"
    monkeypatch.setattr(db, "DATABASE_PATH", test_db_path)
    db.init_db()
    return test_db_path


def test_create_task(test_database):
    """Проверяет создание задачи."""
    task_id = create_task("Подготовить отчёт", "Наталья")

    task = db.get_task_by_id(task_id)

    assert task is not None
    assert task["text"] == "Подготовить отчёт"
    assert task["user"] == "Наталья"
    assert task["status"] == "new"


def test_create_empty_task(test_database):
    """Проверяет запрет создания пустой задачи."""
    with pytest.raises(ValueError):
        create_task("   ", "Наталья")


def test_get_tasks_page(test_database):
    """Проверяет получение страниц задач."""
    for number in range(12):
        create_task(f"Задача {number}", "Наталья")

    first_page, total_pages = get_tasks_page(1)
    second_page, _ = get_tasks_page(2)

    assert len(first_page) == 10
    assert len(second_page) == 2
    assert total_pages == 2


def test_edit_task(test_database):
    """Проверяет изменение текста задачи."""
    task_id = create_task("Старый текст", "Наталья")

    result = edit_task(task_id, "Новый текст")

    assert result is True
    assert db.get_task_by_id(task_id)["text"] == "Новый текст"


def test_change_task_status(test_database):
    """Проверяет изменение статуса задачи."""
    task_id = create_task("Проверить программу", "Наталья")

    result = change_task_status(task_id, "done")

    assert result is True
    assert db.get_task_by_id(task_id)["status"] == "done"


def test_invalid_task_status(test_database):
    """Проверяет отклонение недопустимого статуса."""
    task_id = create_task("Проверить программу", "Наталья")

    with pytest.raises(ValueError):
        change_task_status(task_id, "unknown")


def test_remove_task(test_database):
    """Проверяет удаление задачи."""
    task_id = create_task("Удалить эту задачу", "Наталья")

    result = remove_task(task_id)

    assert result is True
    assert db.get_task_by_id(task_id) is None
