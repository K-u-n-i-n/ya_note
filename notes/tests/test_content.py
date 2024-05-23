from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class BaseNotesTest(TestCase):
    """Базовый тестовый класс для тестов заметок."""
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


class NotesFormsTests(BaseNotesTest):
    """Тесты для проверки отображения заметок в списке для разных поль-лей."""

    def test_notes_list_for_different_users(self):
        """Проверяет отображение заметок пользователей."""
        users_statuses = (
            ('author', True),
            ('not_author', False),
        )

        for user_key, note_in_list in users_statuses:
            with self.subTest(user=user_key):
                response = self.clients[user_key].get(self.url_list_notes)
                notes = response.context['object_list']
                self.assertEqual((self.note in notes), note_in_list)


class NotesPagesTests(BaseNotesTest):
    """Тесты для проверки страниц создания и редактирования заметок."""
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url_add_note = reverse('notes:add')
        cls.url_edit_note = reverse('notes:edit', args=(cls.note.slug,))
        cls.client_author = cls.client_class()
        cls.client_author.force_login(cls.author)

    def test_pages_contains_form(self):
        """Проверяет наличие формы на страницах заметок."""
        urls = (self.url_add_note, self.url_edit_note)
        for url in urls:
            response = self.client_author.get(url)
            with self.subTest(url=url):
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
