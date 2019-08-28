from django.test import TestCase
from django.urls import reverse, resolve
from news import views
from news.models import News, NewsAnswer
from users.models import User, Profile


class MainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('news:main')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/news/')
        self.assertEquals(view.func, views.main_view)


class CreateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('news:create')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/news/create/')
        self.assertEquals(view.func, views.create_news_view)


class DetailTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        # ValueError: Cannot force both insert and updating in model saving.
        # news1 = News.objects.create(title='News 1', slug='news-1', author=self.user1)
        # news1.allowed_profiles |= Profile.objects.filter(id=self.user1)
        self.url = reverse('news:detail', kwargs={'slug': 'news-1'})

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/news/detail:the-good-news/')
        self.assertEquals(view.func, views.news_detail_view)


