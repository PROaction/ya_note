from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заметка'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'new-slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)

        cls.add_url = reverse('notes:add')
        cls.done_url = reverse('notes:success')
        cls.data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'slug': cls.NOTE_SLUG,
        }

    def test_user_can_create_note(self):
        response = self.auth_author.post(self.add_url, data=self.data)
        self.assertRedirects(response, self.done_url)
        note = Note.objects.last()
        actual_notes_count = Note.objects.count()
        self.assertEqual(actual_notes_count, 1)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.author, self.author)

    def test_anon_dont_create_note(self):
        self.client.post(self.add_url, data=self.data)
        actual_notes_count = Note.objects.count()
        self.assertEqual(actual_notes_count, 0)

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=self.author,
        )
        self.data['slug'] = note.slug

        self.client.force_login(self.author)
        response = self.client.post(url, data=self.data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.data.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Заметка'
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'
    NEW_NOTE_TITLE = 'Новый заголовок'
    NEW_NOTE_SLUG = 'new-title'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)

        cls.other_user = User.objects.create(username='Другой пользователь')
        cls.auth_other_user = Client()
        cls.auth_other_user.force_login(cls.other_user)

        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.author,
        )

        cls.note_url = reverse('notes:detail', args=(cls.note.slug, ))
        cls.note_edit_url = reverse('notes:edit', args=(cls.note.slug, ))
        cls.note_delete_url = reverse('notes:delete', args=(cls.note.slug, ))
        cls.note_success_url = reverse('notes:success')

        cls.data = {
            'title': cls.NEW_NOTE_TITLE,
            'slug': cls.NEW_NOTE_SLUG,
            'text': cls.NEW_NOTE_TEXT,
        }

    def test_author_can_edit_note(self):
        response = self.auth_author.post(self.note_edit_url, data=self.data)
        self.assertRedirects(response, self.note_success_url)
        self.note.refresh_from_db()
        actual_note_text = self.note.text
        actual_note_title = self.note.title
        actual_note_slug = self.note.slug
        self.assertEqual(actual_note_text, self.NEW_NOTE_TEXT)
        self.assertEqual(actual_note_title, self.NEW_NOTE_TITLE)
        self.assertEqual(actual_note_slug, self.NEW_NOTE_SLUG)

    def test_author_can_delete_note(self):
        response = self.auth_author.delete(self.note_delete_url)
        self.assertRedirects(response, self.note_success_url)
        actual_notes_count = Note.objects.count()
        self.assertEqual(actual_notes_count, 0)

    def test_other_user_cant_edit_and_delete_note(self):
        expected_note_slug = self.note.slug
        for url in (self.note_edit_url, self.note_delete_url):
            with self.subTest():
                response = self.auth_other_user.post(url, data=self.data)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                self.note.refresh_from_db()
                actual_note_text = self.note.text
                actual_note_title = self.note.title
                actual_note_slug = self.note.slug
                self.assertEqual(actual_note_text, self.NOTE_TEXT)
                self.assertEqual(actual_note_title, self.NOTE_TITLE)
                self.assertEqual(actual_note_slug, expected_note_slug)
