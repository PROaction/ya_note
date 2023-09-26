from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNotesPage(TestCase):
    NOTES_PAGE = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.other_user = User.objects.create(username='Просто пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        authors_note_count = len(Note.objects.all())

        test_datas = (
            (self.author, authors_note_count),
            (self.other_user, 0),
        )
        for user, expected_notes_count in test_datas:
            self.client.force_login(user)
            with self.subTest(name=user):
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
