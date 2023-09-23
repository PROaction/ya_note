from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            author=cls.author,
        )

    def test_pages_available_for_anonymous(self):
        urls = (
            ('notes:home', None),
            ('login', None),
            ('logout', None),
            ('signup', None),
            ('notes:detail', (self.note.id, )),
        )

        for template_name, args in urls:
            print('template_name:', template_name)
            with self.subTest(name=template_name):
                url = reverse(template_name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
