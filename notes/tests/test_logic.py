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
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_user_can_create_note(self):
        """Тест для залогиненного пользователя - может создать заметку."""
        self.client.login(username='author', password='password')
        notes_count_before = Note.objects.count()
        response = self.client.get(self.add_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, User.objects.get(username='author'))

    def test_anonymous_user_cant_create_note(self):
        """Тест для анонимного пользователя - не может создать заметку."""
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.client.login(username='author', password='password')
        form_data = self.form_data.copy()
        form_data['slug'] = self.note.slug
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_empty_slug(self):
        """Тест на автоматическое создание slug."""
        self.client.login(username='author', password='password')
        Note.objects.all().delete()
        form_data = self.form_data.copy()
        form_data.pop('slug')
        notes_count_before = Note.objects.count()
        response = self.client.post(self.add_url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        new_note = Note.objects.get(title=form_data['title'])
        expected_slug = slugify(form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Тест на редактирование своей заметки"""
        self.client.login(username='author', password='password')
        response = self.client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)
