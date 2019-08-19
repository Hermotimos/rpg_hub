from django.test import TestCase
from django.urls import resolve, reverse
from users.views import LoginView, LogoutView, profile_view, register_view, change_password_view


class TestLogin(TestCase):
    # def test_login_view_status_code(self):
    #     url = reverse('users:login')
    #     response = self.client.get(url)
    #     self.assertEquals(response.status_code, 200)

    # def test_login_url_resolves_login_view(self):
    #     view = resolve('/users/login/')
    #     # for class-based views add .view_class cause url ClassBasedView.as_views() creates new function
    #     self.assertEquals(view.func.view_class, LoginView)

    # test login_view() returns 200 (success) status code:
    def test_get(self):
        url = reverse('users:login')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    # test 'login' url resolves login_view():
    def test_url_resolves_view(self):
        view = resolve('/users/login/')
        self.assertEquals(view.func.view_class, LoginView)


class TestLogout(TestCase):
    def test_logout_view_status_code(self):
        url = reverse('users:logout')
        response = self.client.get(url, follow=True)            # follow=True follows beyond @login_required
        self.assertEquals(response.status_code, 200)

    def test_logout_url_resolves_logout_view(self):
        view = resolve('/users/logout/')
        # for class-based views add .view_class cause url ClassBasedView.as_views() creates new function
        self.assertEquals(view.func.view_class, LogoutView)


class TestProfile(TestCase):
    def test_profile_view_status_code(self):
        url = reverse('users:profile')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_profile_url_resolves_profile_view(self):
        view = resolve('/users/profile/')
        self.assertEquals(view.func, profile_view)


class TestRegister(TestCase):
    def test_register_view_status_code(self):
        url = reverse('users:register')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_register_url_resolves_register_view(self):
        view = resolve('/users/register/')
        self.assertEquals(view.func, register_view)


class TestChangePassword(TestCase):
    def test_change_password_view_status_code(self):
        url = reverse('users:change-password')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_change_password_url_resolves_change_password_view(self):
        view = resolve('/users/profile/change_password/')
        self.assertEquals(view.func, change_password_view)
