from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestNotesPage(TestCase):
    NOTES_PAGE = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.other_user = User.objects.create(username='Просто пользователь')
        cls.other_client = Client()
        cls.other_client.force_login(cls.other_user)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        user_clients = (
            (self.author_client, True),
            (self.other_client, False),
        )
        for user_client, notes_has_note in user_clients:
            with self.subTest(name=user_client):
                response = user_client.get(self.NOTES_PAGE)
                notes = response.context['note_list']
                self.assertEqual(self.note in notes, notes_has_note)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug, )),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context.get('form'), NoteForm
                )
