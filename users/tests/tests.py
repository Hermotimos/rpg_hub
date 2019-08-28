from django.test import TestCase
from django.urls import resolve, reverse
from users import views
from users.models import User


class TestLogin(TestCase):
    def test_get(self):
        self.url = reverse('users:login')
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/users/login/')
        # for class-based views add .view_class cause url ClassBasedView.as_views() creates new function
        self.assertEquals(view.func.view_class, views.LoginView)


class TestRegister(TestCase):
    def test_get(self):
        url = reverse('users:register')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/users/register/')
        self.assertEquals(view.func, views.register_view)


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
