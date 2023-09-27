from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        authors_note_count = Note.objects.count()

        test_datas = (
            (self.author_client, authors_note_count),
            (self.other_client, 0),
        )
        for user_client, expected_notes_count in test_datas:
            self.client.force_login(user_client)
            with self.subTest(name=user_client):
                response = self.client.get(self.NOTES_PAGE)
                note_list = response.context['note_list']
                actual_note_count = len(note_list)
                self.assertEqual(actual_note_count, expected_notes_count)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug, )),
        )

        for name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
