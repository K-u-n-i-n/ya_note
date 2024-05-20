from http import HTTPStatus
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


# from django.conf import settings
# from django.test import TestCase
# # Импортируем функцию для получения модели пользователя.
# from django.contrib.auth import get_user_model
# # Импортируем функцию reverse(), она понадобится для получения адреса страницы.
# from django.urls import reverse


# from notes.models import Note

# # Импортируем класс формы.
# from notes.forms import NoteForm


# User = get_user_model()


# #  Необходимо доделать работу!!!!!!!!!!!!!!!!!!!!!!!!

# # Что в контексте лежит правильный ключ
# # 2. Что выводится на страницу тоже число заметок, что и создана
# # 3. Что страница используется правильный шаблон
# # 4. Что страница открывается гостем с нужным кодом ответа


# class TestHomePage(TestCase):
#     # Вынесем ссылку на домашнюю страницу в атрибуты класса.
#     LIST_URL = reverse('notes:list')

#     @classmethod
#     def setUpTestData(cls):  # Групповое создание объектов (10 шт).
#         # Создаём пользователя:
#         cls.author = User.objects.create(username='Александр Бунин')
#         cls.all_note = [
#             Note(
#                 title=f'Новость {index}',
#                 text='Текст',
#                 slug=f'nov{index}',
#                 author_id=1
#             )
#             for index in range(11)
#         ]
#         Note.objects.bulk_create(cls.all_note)

#     def test_notes_count(self):
#         # Проверяем количество заметок на странице
#         notes_count = Note.objects.count()
#         self.assertEqual(notes_count, 10)
