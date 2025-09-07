# отдельная заметка передаётся на страницу со списком заметок в списке object_list, в словаре context;
# в список заметок одного пользователя не попадают заметки другого пользователя;
# на страницы создания и редактирования заметки передаются формы.
import pytest

from notes.forms import NoteForm

from django.urls import reverse


@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, note_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False),
    )
)
# Используем фикстуру заметки и параметры из декоратора:
def test_notes_list_for_different_users(
    note, parametrized_client, note_in_list
):
    """Тест на отображение заметки автора в списках.

    Выполняются следующие проверки:
    1. Отдельная заметка передаётся на страницу со списком заметок 
    в списке object_list, в словаре context.
    2. В список заметок одного пользователя не попадают заметки другого 
    пользователя;
    """
    url = reverse('notes:list')
    # Выполняем запрос от имени параметризованного клиента:
    response = parametrized_client.get(url)
    object_list = response.context['object_list']
    # Проверяем истинность утверждения "заметка есть в списке":
    assert (note in object_list) is note_in_list

@pytest.mark.parametrize(
    # В качестве параметров передаём name и args для reverse.
    'name, args',
    (
        # Для тестирования страницы создания заметки 
        # никакие дополнительные аргументы для reverse() не нужны.
        ('notes:add', None),
        # Для тестирования страницы редактирования заметки нужен slug заметки.
        ('notes:edit', pytest.lazy_fixture('slug_for_args'))
    )
)
def test_pages_contains_form(author_client, name, args):
    """Тест на наличие формы на страницах создания и редактирования заметки."""
    # Формируем URL.
    url = reverse(name, args=args)
    # Запрашиваем нужную страницу:
    response = author_client.get(url)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], NoteForm) 
