from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс комментария.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):
    """Тестирование путей.

    1. Главная страница доступна анонимному пользователю.
    2. Страница отдельной заметки недоступна анонимному пользователю.
    3. Страницы удаления и редактирования заметки доступны автору комментария.
    4. При попытке перейти на страницу редактирования или удаления комментария
        анонимный пользователь перенаправляется на страницу авторизации.
    5. Авторизованный пользователь не может зайти на страницу редактирования
        или удаления чужих заметок (возвращается ошибка 404).
    6. Страницы регистрации пользователей, входа в учётную запись доступны
        анонимным пользователям.
    """

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.another_author = User.objects.create(username='Другой автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )

    def test_pages_available_to_anonymous(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_detail_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.another_author, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:detail', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name in ('notes:edit', 'notes:detail', 'notes:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
