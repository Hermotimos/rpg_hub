from django.test import TestCase
from django.urls import reverse, resolve
from home import views
from users.models import User


class LinksToAppsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('home:home')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/')
        self.assertEquals(view.func, views.home_view)

    def test_contains_link_to_apps(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)

        # for non-game-master users:
        self.assertContains(response, f'href="{reverse("news:main")}"')
        self.assertContains(response, f'href="{reverse("rules:main")}"')
        self.assertContains(response, f'href="{reverse("contact:demands-main")}"')
        self.assertContains(response, f'href="{reverse("history:chronicle-main")}"')
        self.assertContains(response, f'href="{reverse("history:timeline-main")}"')
        self.assertContains(response, f'href="{reverse("debates:main")}"')
        self.assertContains(response, f'href="{reverse("users:logout")}"')
        self.assertContains(response, f'href="{reverse("contact:demands-create")}"')
        self.assertContains(response, f'href="{reverse("contact:plans-main")}"')
        self.assertContains(response, f'href="{reverse("users:profile")}"')

        # for game-master users:
        self.user1.profile.character_status = 'gm'
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{reverse("admin:index")}"')
