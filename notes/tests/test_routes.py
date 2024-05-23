from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class NotesTests(TestCase):
    """Тесты для проверки доступности страниц заметок."""

    @classmethod
    def setUpTestData(cls):
        """
        Создание тестовых пользователей и заметки.

        Метод:
        1. Создаем двух пользователей: автора и не автора.
        2. Создаем заметку, принадлежащую автору.
        3. Создаем клиентов и логиним их.
        """
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.client_author = cls.client_class()
        cls.client_author.force_login(cls.author)
        cls.client_not_author = cls.client_class()
        cls.client_not_author.force_login(cls.not_author)

    def test_pages_availability_for_anonymous_user(self):
        """
        Проверяет доступность страниц для анонимного пользователя.

        Метод:
        1. Перебираем URL страниц, доступных для анонимного пользователя.
        2. Для каждой страницы отправляем GET-запрос и проверяем,
        что статус ответа HTTP 200 (OK).
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """
        Проверяет доступность страниц для аутентифицированного пользователя.

        Метод:
        1. Перебираем URL страниц, доступных для аутентифицированного
        пользователя.
        2. Для каждой страницы отправляем GET-запрос от имени не автора
        и проверяем, что статус ответа HTTP 200 (OK).
        """
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client_not_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """
        Проверяет доступность страниц заметок для разных пользователей.

        Метод:
        1. Перебираем пары (пользователь, ожидаемый статус ответа).
        2. Логинимся под каждым пользователем и проверяем доступность страниц.
        3. Для каждой страницы проверяем, соответствует ли статус ответа
        ожидаемому значению.
        """
        clients_statuses = (
            (self.client_not_author, HTTPStatus.NOT_FOUND),
            (self.client_author, HTTPStatus.OK),
        )
        for client, status in clients_statuses:
            for name in ('notes:detail', 'notes:edit', 'notes:delete'):
                with self.subTest(client=client, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirects_for_anonymous_user(self):
        """
        Проверяет перенаправления для анонимного пользователя.

        Метод:
        1. Перебираем URL страниц, требующих аутентификации.
        2. Для каждой страницы отправляем GET-запрос от анонимного
        пользователя.
        3. Проверяем, что происходит перенаправление на страницу логина с
        параметром next, содержащим запрашиваемый URL.
        """
        login_url = reverse('users:login')
        urls_args = (
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        for name, args in urls_args:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
