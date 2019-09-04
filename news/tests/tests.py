from django.test import TestCase
from django.urls import reverse, resolve
from news import views
from news.models import News, NewsAnswer
from news.forms import CreateNewsForm, CreateNewsAnswerForm
from users.models import User


class MainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')

        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'

        self.news1 = News.objects.create(id=1, title='Title1', author=self.user1)
        self.news1.allowed_profiles.set([self.user1.profile, ])
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

    def test_links(self):
        linked_url1 = reverse('news:create')
        linked_url2 = reverse('news:detail', kwargs={'news_id': self.news1.id})

        # case request.user.profile in news.allowed_profiles
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')

        # case request.user.profile not in news.allowed_profiles
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')

        # case request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')


class CreateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'active_player'
        self.user2.save()

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

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, CreateNewsForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'author': self.user1.id,
            'title': 'News1',
            'text': 'news1',
            'allowed_profiles': [self.user2.id, ]
        }
        self.client.post(self.url, data)
        self.assertTrue(News.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(News.objects.count() == 0)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'text': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(News.objects.count() == 0)


class DetailTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        self.news1 = News.objects.create(id=1, title='News1', text='news1', author=self.user1)
        self.news1.allowed_profiles.set([self.user1.profile, self.user2.profile, ])
        self.news1.followers.set([self.user1.profile, ])
        self.url = reverse('news:detail', kwargs={'news_id': self.news1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('news:detail', kwargs={'news_id': self.news1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/news/detail:{self.news1.id}/')
        self.assertEquals(view.func, views.news_detail_view)

    def test_links(self):
        linked_url1 = reverse('news:unfollow', kwargs={'news_id': self.news1.id})
        linked_url2 = reverse('news:follow', kwargs={'news_id': self.news1.id})

        # case request.user.profile in news1.followers.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')

        # case request.user.profile not in news1.followers.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertNotContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, CreateNewsAnswerForm)

    def test_valid_post_data(self):               # TODO still doesn't pass - user2.profile is not presented in choices
        self.client.force_login(self.user1)
        data = {
            'text': 'news1',
        }
        self.client.post(self.url, data)
        self.assertTrue(NewsAnswer.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(NewsAnswer.objects.count() == 0)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'text': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(NewsAnswer.objects.count() == 0)


class FollowNewsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.news1 = News.objects.create(id=1, title='News1', text='news1', author=self.user1)
        self.news1.allowed_profiles.set([self.user1.profile, ])
        self.url = reverse('news:follow', kwargs={'news_id': self.news1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('news:follow', kwargs={'news_id': self.news1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed(self):
        self.client.force_login(self.user1)
        redirect_url = reverse('news:detail', kwargs={'news_id': self.news1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # No test_get - no template generated by follow_news_view()

    def test_url_resolves_view(self):
        view = resolve(f'/news/detail:{self.news1.id}/follow')
        self.assertEquals(view.func, views.follow_news_view)


class UnfollowNewsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.news1 = News.objects.create(id=1, title='News1', text='news1', author=self.user1)
        self.news1.allowed_profiles.set([self.user1.profile, ])
        self.url = reverse('news:follow', kwargs={'news_id': self.news1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('news:unfollow', kwargs={'news_id': self.news1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed(self):
        self.client.force_login(self.user1)
        redirect_url = reverse('news:detail', kwargs={'news_id': self.news1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # No test_get - no template generated by unfollow_news_view()

    def test_url_resolves_view(self):
        view = resolve(f'/news/detail:{self.news1.id}/unfollow')
        self.assertEquals(view.func, views.unfollow_news_view)



