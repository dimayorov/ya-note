from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import unittest

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestCreateUpdatePage(TestCase):
    """Тестирование содержания.

    1. Анонимному пользователю не видна форма для отправки заметки на странице
        отдельной новости, а авторизованному видна.
    """

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заметка',
            text='Просто текст.',
            slug='slug',
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_anonymous_client_has_no_form(self):

        for name in ('notes:add', 'notes:edit'):
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        for name, arg in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        ):
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=arg))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
