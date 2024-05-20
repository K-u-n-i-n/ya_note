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

    # Тест для проверки, что в список заметок одного пользователя
    # не попадают заметки другого пользователя.
    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author, True),
            (self.not_author, False),
        )
        for user, note_in_list in users_statuses:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            with self.subTest(user=user):
                self.assertEqual((self.note in object_list), note_in_list)

    # Тест для проверки, что на страницы создания и редактирования
    # заметки передаются формы.
    def test_pages_contains_form(self):
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
