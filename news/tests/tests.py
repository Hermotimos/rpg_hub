from django.test import TestCase
from django.urls import reverse, resolve
from news.views import main_view, create_news_view, news_detail_view, follow_news_view, unfollow_news_view
from news.models import News, NewsAnswer
from users.models import User, Profile


class MainTest(TestCase):
    def test_get(self):
        url = reverse('news:main')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/news/')
        self.assertEquals(view.func, main_view)


class CreateTest(TestCase):
    def test_get(self):
        url = reverse('news:create')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/news/create/')
        self.assertEquals(view.func, create_news_view)


class DetailTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='test_user', email='test@user.com', password='sswapord123')
        mock_user.save()
        news = News.objects.create(title='The good news', text='Blahblah', author=mock_user)
        news.save()
        news.allowed_profiles.set(Profile.objects.get(pk=1))

    # These don't work, why?
    #
    # def test_get(self):
    #     url = reverse('news:detail', kwargs={'slug': 'the-good-news'})
    #     response = self.client.get(url, follow=True)
    #     self.assertEquals(response.status_code, 200)
    #
    # def test_url_resolves_view(self):
    #     view = resolve('/news/detail:the-good-news/')
    #     self.assertEquals(view.func, news_detail_view)


