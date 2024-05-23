from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class NotesFormsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='author', password='password')
        cls.other_user = User.objects.create_user(
            username='other', password='password')
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
        cls.other_note = Note.objects.create(
            title='Other Title',
            text='Other Text',
            slug='other-slug',
            author=cls.other_user,
        )
        cls.add_url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')

    def setUp(self):
        self.client.login(username='author', password='password')

    def test_user_can_create_note(self):
        """Тест для залогиненного пользователя - может создать заметку."""
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Тест для анонимного пользователя - не может создать заметку."""
        self.client.logout()
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        url = reverse('notes:add')
        form_data = self.form_data.copy()
        form_data['slug'] = self.note.slug
        response = self.client.post(url, data=form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Тест на автоматическое создание slug."""
        url = reverse('notes:add')
        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 2)
        new_note = Note.objects.latest('id')
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Тест на редактирование своей заметки"""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_author_can_delete_note(self):
        """Тест на удаление своей заметки."""
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_edit_others_note(self):
        """Тест на невозможность редактирования чужой заметки."""
        other_note = self.create_other_user_and_note()
        url = reverse('notes:edit', args=(other_note.slug,))
        response = self.client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        other_note.refresh_from_db()
        self.assertNotEqual(other_note.title, self.form_data['title'])

    def test_user_cant_delete_others_note(self):
        """Тест на невозможность удаления чужой заметки."""
        other_note = self.create_other_user_and_note()
        url = reverse('notes:delete', args=(other_note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 2)
