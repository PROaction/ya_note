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

        cls.personal_urls = (
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
            ('notes:detail', (cls.note.slug,)),
        )

        cls.login_only_urls = (
            ('notes:add', None),
            *cls.personal_urls,
            ('notes:list', None),
            ('notes:success', None),
        )

        cls.all_available_urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )

        cls.urls = (
            *cls.all_available_urls,
            *cls.login_only_urls,
            ('notes:list', None),
        )

    def check_redirect(self, response, url):
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)

    def test_available_pages_for_anonymous(self):
        status_check = (
            (self.all_available_urls, HTTPStatus.OK),
            (self.login_only_urls, HTTPStatus.FOUND),
        )

        for urls, expected_status_code in status_check:
            for name, args in urls:
                with self.subTest():
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    actual_status_code = response.status_code
                    self.assertEqual(actual_status_code, expected_status_code)
                    if actual_status_code == HTTPStatus.FOUND:
                        self.check_redirect(response, url)

    def test_pages_availability_for_auth_user(self):
        for name, args in self.urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_personal_interaction_for_notes(self):
        users_status = (
            (self.author, HTTPStatus.OK),
            (self.other_user, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_status:
            self.client.force_login(user)
            for name, args in self.personal_urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
