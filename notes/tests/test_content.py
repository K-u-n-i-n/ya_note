from django.conf import settings
from django.test import TestCase
# Импортируем функцию для получения модели пользователя.
from django.contrib.auth import get_user_model
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse


from notes.models import Note

# Импортируем класс формы.
from notes.forms import NoteForm


User = get_user_model()



#  Необходимо доделать работу!!!!!!!!!!!!!!!!!!!!!!!!

# Что в контексте лежит правильный ключ
# 2. Что выводится на страницу тоже число заметок, что и создана
# 3. Что страница используется правильный шаблон
# 4. Что страница открывается гостем с нужным кодом ответа


class TestHomePage(TestCase):
    # Вынесем ссылку на домашнюю страницу в атрибуты класса.
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):  # Групповое создание объектов (10 шт).
        # Создаём пользователя:
        cls.author = User.objects.create(username='Александр Бунин')
        cls.all_note = [
            Note(
                title=f'Новость {index}',
                text='Текст',
                slug=f'nov{index}',
                author_id=1
            )
            for index in range(11)
        ]
        Note.objects.bulk_create(cls.all_note)

    def test_notes_count(self):
        # Проверяем количество заметок на странице
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 10)
