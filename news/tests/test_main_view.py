from django.test import TestCase
from django.urls import reverse, resolve
from news import views
from news.models import News, Survey
from users.models import User


class MainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.status = 'gm'
        self.user4.profile.save()

        self.news1 = News.objects.create(title='Title1', author=self.user1)
        self.news1.allowed_profiles.set([self.user1.profile, self.user2.profile])
        self.survey1 = Survey.objects.create(title='Survey1', author=self.user1)
        self.survey1.addressees.set([self.user1.profile, self.user2.profile])

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
        linked_url3 = reverse('news:survey-detail', kwargs={'survey_id': self.survey1.id})

        # request.user.profile in news1.allowed_profiles.all() and is survey1.author
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')

        # request.user.profile in news1.allowed_profiles and survey1.addressees.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')

        # request.user.profile not in news1.allowed_profiles.all() and not in survey1.addressees.all()
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')

        # request.user.profile.status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
