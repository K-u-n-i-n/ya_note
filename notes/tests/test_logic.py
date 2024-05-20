from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class NotesFormsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author', password='password')
        cls.form_data = {
            'title': 'Test Title',
            'text': 'Test Text',
            'slug': 'test-slug',
        }
        cls.note = Note.objects.create(
            title='Existing Title',
            text='Existing Text',
            slug='existing-slug',
            author=cls.author,
        )

    def setUp(self):
        self.client.login(username='author', password='password')

    def create_other_user_and_note(self):
        other_user = User.objects.create_user(
            username='other', password='password'
        )
        other_note = Note.objects.create(
            title='Other Title',
            text='Other Text',
            slug='other-slug',
            author=other_user,
        )
        return other_note

    # Тест для залогиненного пользователя - может создать заметку.
    def test_user_can_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.latest('id')
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    # Тест для анонимного пользователя - не может создать заметку.
    def test_anonymous_user_cant_create_note(self):
        self.client.logout()
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    # 2. Невозможно создать две заметки с одинаковым slug.
    def test_not_unique_slug(self):
        url = reverse('notes:add')
        form_data = self.form_data.copy()
        form_data['slug'] = self.note.slug
        response = self.client.post(url, data=form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    # Тест на автоматическое создание slug.
    def test_empty_slug(self):
        url = reverse('notes:add')
        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    # Тест на редактирование своей заметки
    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    # Тест на удаление своей заметки.
    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    # Тест на невозможность редактирования чужой заметки.
    def test_user_cant_edit_others_note(self):
        other_note = self.create_other_user_and_note()
        url = reverse('notes:edit', args=(other_note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        other_note.refresh_from_db()
        self.assertNotEqual(other_note.title, self.form_data['title'])

    # Тест на невозможность удаления чужой заметки.
    def test_user_cant_delete_others_note(self):
        other_note = self.create_other_user_and_note()
        url = reverse('notes:delete', args=(other_note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 2)
