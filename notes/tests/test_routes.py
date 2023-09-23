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
        cls.other_user = User.objects.create(username='Просто пользователь')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            author=cls.author,
        )

    def check_redirect(self, response, url):
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)

    def test_available_pages_for_anonymous(self):
        available_urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        login_only_urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
        )

        status_check = (
            (available_urls, HTTPStatus.OK),
            (login_only_urls, HTTPStatus.FOUND),
        )

        for urls, expected_status_code in status_check:
            for name, args in urls:
                url = reverse(name, args=args)
                response = self.client.get(url)
                actual_status_code = response.status_code
                self.assertEqual(actual_status_code, expected_status_code)
                if actual_status_code == HTTPStatus.FOUND:
                    self.check_redirect(response, url)

    def test_personal_CRUD_for_notes(self):
        users_status = (
            (self.author, HTTPStatus.OK),
            (self.other_user, HTTPStatus.NOT_FOUND),
        )
        personal_urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
        )
        for user, status in users_status:
            self.client.force_login(user)
            for name, args in personal_urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)


    #
    #     for name, args in available_urls:
    #         print('template_name:', name)
    #         with self.subTest(name=name):
    #             url = reverse(name, args=args)
    #             response = self.client.get(url)
    #             self.assertEqual(response.status_code, HTTPStatus.OK)
    #
    # def test_available_pages_for_anonymous(self):
    #     urls = (
    #         ('notes:add', None),
    #         ('notes:edit', (self.note.slug, )),
    #         ('notes:delete', (self.note.slug, )),
    #         ('notes:detail', (self.note.slug,)),
    #         ('notes:list', None),
    #     )
    #
    #     for name, args in urls:

