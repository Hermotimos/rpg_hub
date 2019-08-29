from django.test import TestCase
from django.urls import resolve, reverse
from users import views
from users.models import User


class TestLogin(TestCase):
    def setUp(self):
        self.url = reverse('users:login')
        self.response = self.client.get(self.url)

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/users/login/')
        # for class-based views add .view_class cause url ClassBasedView.as_views() creates new function
        self.assertEquals(view.func.view_class, views.LoginView)

    def test_contains_links(self):
        linked_url = reverse('users:register')
        self.assertContains(self.response, f'href="{linked_url}"')


class TestRegister(TestCase):
    def setUp(self):
        self.url = reverse('users:register')
        self.response = self.client.get(self.url)

    def test_get(self):
        url = reverse('users:register')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/users/register/')
        self.assertEquals(view.func, views.register_view)

    def test_contains_links(self):
        linked_url = reverse('users:login')
        self.assertContains(self.response, f'href="{linked_url}"')


class TestLogout(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('users:logout')

    def test_redirect_to_login_after_logout(self):
        self.client.force_login(self.user1)
        redirect_url = reverse('users:login')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_url_resolves_view(self):
        view = resolve('/users/logout/')
        # for class-based views add .view_class cause url ClassBasedView.as_views() creates new function
        self.assertEquals(view.func.view_class, views.LogoutView)


class TestProfile(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('users:profile')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/users/profile/')
        self.assertEquals(view.func, views.profile_view)

    def test_contains_links(self):
        self.client.force_login(self.user1)
        linked_url = reverse('users:change-password')
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url}"')


class TestChangePassword(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('users:change-password')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/users/profile/change_password/')
        self.assertEquals(view.func, views.change_password_view)
