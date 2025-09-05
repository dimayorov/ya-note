from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):

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
        cls.success_url = reverse('notes:success', None)
        cls.create_url = reverse('notes:add', None)
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Просто текст',
            'slug': 'slug_new',
        }

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.create_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.create_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_user_cant_use_same_slug(self):
        dublicate_form_data = {
            'title': 'Заголовок',
            'text': 'Просто текст',
            'slug': 'slug',
        }
        response = self.auth_client.post(
            self.create_url,
            data=dublicate_form_data,
        )
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFormError(
            form=form,
            field='slug',
            errors='slug' + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text=cls.NOTE_TEXT,
            slug='slug',
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_author = User.objects.create(username='Другой автор')
        cls.another_author_client = Client()
        cls.another_author_client.force_login(cls.another_author)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success', None)
        cls.form_data = {
            'title': 'Заголовок',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'slug',
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.another_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.another_author_client.post(
            self.edit_url,
            data=self.form_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
