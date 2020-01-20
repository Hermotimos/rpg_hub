from django.test import TestCase
from django.urls import reverse, resolve
from news import views
from news.models import News, NewsAnswer
from news.forms import CreateNewsForm, CreateNewsAnswerForm
from users.models import User
