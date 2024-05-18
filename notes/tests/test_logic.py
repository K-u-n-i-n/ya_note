from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

# ДОДЕЛАТЬ!!!!!!!!!!!!!!!!!!!!!!!!!!!!