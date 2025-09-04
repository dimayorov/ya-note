from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
import unittest

# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Текст комментария'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заметка',
            text='Просто текст.',
            slug='slug',
        )

        cls.url = reverse('notes:detail', args=(cls.note.slug,))
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Просто текст',
            'slug': 'slug_new',
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    # @unittest.skip('Временно загашено.')
    # def test_user_can_create_note(self):
    #     response = self.auth_client.post(self.url, data=self.form_data)
    #     self.assertRedirects(response, self.url)
    #     notes_count = Note.objects.count()
    #     self.assertEqual(notes_count, 2)
        # note = Note.objects.get()
        # self.assertEqual(note.text, self.text)
        # self.assertEqual(note.title, self.title)
        # self.assertEqual(note.slug, self.slug)
        # self.assertEqual(note.author, self.author)

    # @unittest.skip('Временно загашено.')
    # def test_user_cant_use_same_slug(self):
    #     # Формируем данные для отправки формы; текст включает
    #     # первое слово из списка стоп-слов.
    #     # bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    #     # Отправляем запрос через авторизованный клиент.
    #     response = self.auth_client.post(self.url)
    #     form = response.context['form']
    #     # Проверяем, есть ли в ответе ошибка формы.
    #     self.assertFormError(
    #         form=form,
    #         field='slug',
    #         errors=WARNING
    #     )
    #     # Дополнительно убедимся, что комментарий не был создан.
    #     notes_count = Note.objects.count()
    #     self.assertEqual(notes_count, 0)

# @unittest.skip('Временно загашено.')
# class TestNoteEditDelete(TestCase):
#     # Тексты для комментариев не нужно дополнительно создавать
#     # (в отличие от объектов в БД), им не нужны ссылки на self или cls,
#     # поэтому их можно перечислить просто в атрибутах класса.
#     NOTE_TEXT = 'Текст комментария'
#     NEW_NOTE_TEXT = 'Обновлённый комментарий'

#     @classmethod
#     def setUpTestData(cls):
#         # Создаём новость в БД.
#         cls.note = Note.objects.create(
#             title='Заголовок',
#             text='Текст',
#             slug='slug',
#         )
#         # Формируем адрес блока с комментариями, который понадобится для тестов
#         note_url = reverse('notes:detail', args=(cls.note.slug,))  # Адрес новости
#         cls.url_to_note = note_url  # Адрес блока с коммент.
#         # Создаём пользователя - автора комментария.
#         cls.author = User.objects.create(username='Автор заметки')
#         # Создаём клиент для пользователя-автора.
#         cls.author_client = Client()
#         # "Логиним" пользователя в клиенте.
#         cls.author_client.force_login(cls.author)
#         # Делаем всё то же самое для пользователя-читателя.
#         cls.another_author = User.objects.create(username='Другой автор')
#         cls.another_author_client = Client()
#         cls.another_author_client.force_login(cls.another_author)
#         # Создаём объект комментария.
#         cls.note = Note.objects.create(
#             note=cls.note,
#             author=cls.author,
#             text=cls.text
#         )
#         # URL для редактирования комментария.
#         cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
#         # URL для удаления комментария.
#         cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
#         # Формируем данные для POST-запроса по обновлению комментария.
#         cls.form_data = {'text': cls.NEW_NOTE_TEXT}

    # @unittest.skip('Временно загашено.')
    # def test_author_can_delete_note(self):
    #     # От имени автора комментария отправляем DELETE-запрос на удаление.
    #     response = self.author_client.delete(self.delete_url)
    #     # Проверяем, что редирект привёл к разделу с комментариями.
    #     self.assertRedirects(response, self.url_to_note)
    #     # Заодно проверим статус-коды ответов.
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    #     # Считаем количество комментариев в системе.
    #     notes_count = Note.objects.count()
    #     # Ожидаем ноль комментариев в системе.
    #     self.assertEqual(notes_count, 0)

    # @unittest.skip('Временно загашено.')
    # def test_user_cant_delete_note_of_another_user(self):
    #     # Выполняем запрос на удаление от пользователя-читателя.
    #     response = self.reader_client.delete(self.delete_url)
    #     # Проверяем, что вернулась 404 ошибка.
    #     self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    #     # Убедимся, что комментарий по-прежнему на месте.
    #     notes_count = Note.objects.count()
    #     self.assertEqual(notes_count, 1)

    # @unittest.skip('Временно загашено.')
    # def test_author_can_edit_note(self):
    #     # Выполняем запрос на редактирование от имени автора комментария.
    #     response = self.author_client.post(self.edit_url, data=self.form_data)
    #     # Проверяем, что сработал редирект.
    #     self.assertRedirects(response, self.url_to_note)
    #     # Обновляем объект комментария.
    #     self.note.refresh_from_db()
    #     # Проверяем, что текст комментария соответствует обновленному.
    #     self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    # @unittest.skip('Временно загашено.')
    # def test_user_cant_edit_note_of_another_user(self):
    #     # Выполняем запрос на редактирование от имени другого пользователя.
    #     response = self.reader_client.post(self.edit_url, data=self.form_data)
    #     # Проверяем, что вернулась 404 ошибка.
    #     self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
    #     # Обновляем объект комментария.
    #     self.note.refresh_from_db()
    #     # Проверяем, что текст остался тем же, что и был.
    #     self.assertEqual(self.note.text, self.NOTE_TEXT)
