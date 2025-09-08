import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from pytils.translit import slugify
from http import HTTPStatus
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


def test_user_can_create_note(author_client, author, form_data):
    """Тест на возможность создать заметку авторизованным пользователем."""
    url = reverse('notes:add')
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    assert new_note.title == form_data['title']
    assert new_note.text == form_data['text']
    assert new_note.slug == form_data['slug']
    assert new_note.author == author

@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client, form_data):
    """Тест на невозможность создать заметку неавторизованным пользователем."""
    url = reverse('notes:add')
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Note.objects.count() == 0

def test_not_unique_slug(author_client, note, form_data):
    """Тест на уникальность slug заметки."""
    url = reverse('notes:add')
    form_data['slug'] = note.slug
    response = author_client.post(url, data=form_data)
    assertFormError(
        response.context['form'], 'slug', errors=(note.slug + WARNING)
    )
    assert Note.objects.count() == 1

def test_empty_slug(author_client, form_data):
    """Тест на создание заметки с пустым slug."""
    url = reverse('notes:add')
    form_data.pop('slug')
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 1
    new_note = Note.objects.get()
    expected_slug = slugify(form_data['title'])
    assert new_note.slug == expected_slug

def test_author_can_edit_note(author_client, form_data, note):
    """Тест на возможность редактирования заметки автором."""
    url = reverse('notes:edit', args=(note.slug,))
    response = author_client.post(url, form_data)
    assertRedirects(response, reverse('notes:success'))
    note.refresh_from_db()
    assert note.title == form_data['title']
    assert note.text == form_data['text']
    assert note.slug == form_data['slug']

def test_other_user_cant_edit_note(not_author_client, form_data, note):
    """Тест на невозможность редактирования заметки другим пользователем."""
    url = reverse('notes:edit', args=(note.slug,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    note_from_db = Note.objects.get(id=note.id)
    assert note.title == note_from_db.title
    assert note.text == note_from_db.text
    assert note.slug == note_from_db.slug

def test_author_can_delete_note(author_client, slug_for_args):
    """Тест на возможность удаления заметки пользователем."""
    url = reverse('notes:delete', args=slug_for_args)
    response = author_client.post(url)
    assertRedirects(response, reverse('notes:success'))
    assert Note.objects.count() == 0


def test_other_user_cant_delete_note(not_author_client, slug_for_args):
    """Тест на невозможность удаления заметки другим пользователем."""
    url = reverse('notes:delete', args=slug_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Note.objects.count() == 1
