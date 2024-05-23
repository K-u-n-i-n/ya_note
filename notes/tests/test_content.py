from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class NotesFormsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.url_list_notes = reverse('notes:list')
        cls.clients = {
            'author': cls.client_class(),
            'not_author': cls.client_class(),
        }
        cls.clients['author'].force_login(cls.author)
        cls.clients['not_author'].force_login(cls.not_author)

    def test_notes_list_for_different_users(self):
        """
        Тест для проверки, что в список заметок одного пользователя
        не попадают заметки другого пользователя.
        """
        users_statuses = (
            ('author', True),
            ('not_author', False),
        )

        for user_key, note_in_list in users_statuses:
            with self.subTest(user=user_key):
                response = self.clients[user_key].get(self.url_list_notes)
                notes = response.context['object_list']
                self.assertEqual((self.note in notes), note_in_list)

    def test_pages_contains_form(self):
        """
        Тест для проверки, что на страницы создания и редактирования
        заметки передаются формы.
        """
        urls_args = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls_args:
            url = reverse(name, args=args)
            response = self.client.get(url)
            with self.subTest(name=name):
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
