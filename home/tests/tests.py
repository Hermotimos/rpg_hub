from django.test import TestCase
from django.urls import reverse, resolve
from home import views
from users.models import User


class TestHome(TestCase):
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


class ContainsNavbarAndSidebarLinks(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.client.force_login(self.user1)
        self.url = reverse('home:home')
        self.response = self.client.get(self.url)

    def test_contains_navbar_and_sidebar_links(self):
        # NAVBAR:
        self.assertContains(self.response, f'href="{reverse("home:home")}"')
        self.assertContains(self.response, f'href="{reverse("news:main")}"')
        self.assertContains(self.response, f'href="{reverse("rules:main")}"')
        self.assertContains(self.response, f'href="{reverse("contact:demands-main")}"')
        self.assertContains(self.response, f'href="{reverse("history:chronicle-main")}"')
        self.assertContains(self.response, f'href="{reverse("history:timeline-main")}"')
        self.assertContains(self.response, f'href="{reverse("debates:main")}"')
        self.assertContains(self.response, f'href="{reverse("users:profile")}"')
        self.assertContains(self.response, f'href="{reverse("contact:demands-create")}"')
        self.assertContains(self.response, f'href="{reverse("users:logout")}"')

        # SIDEBAR - for all users:
        self.assertContains(self.response, f'href="{reverse("contact:plans-main")}"')

        # SIDEBAR - for non-game-master users:

        # SIDEBAR - for game-master users:
        self.user1.profile.character_status = 'gm'
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{reverse("admin:index")}"')
        self.assertContains(response, f'href="{reverse("history:chronicle-create")}"')
        self.assertContains(response, f'href="{reverse("history:timeline-create")}"')
        self.assertContains(response, f'href="{reverse("contact:plans-for-gm")}"')
