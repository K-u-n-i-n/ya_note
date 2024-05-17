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


class TestHomePage(TestCase):
    # Вынесем ссылку на домашнюю страницу в атрибуты класса.
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):  # Групповое создание объектов (11 шт).
        # Создаём пользователя:
        cls.author = User.objects.create(username='Александр Бунин')
        cls.all_note = [
            Note(
                title=f'Новость {index}',
                text='Текст',
                slug=f'nov{index}',
                author_id=1
            )
            for index in range(10)
        ]
        Note.objects.bulk_create(cls.all_note)

    def test_note_count(self):  # Проверяем количество объектов на странице.
        # Загружаем страницу с заметками.
        response = self.client.get(self.LIST_URL)
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем количество записей в списке.
        note_count = object_list.count()
        # Проверяем, что на странице именно 10 новостей.
        self.assertEqual(note_count, 10)
