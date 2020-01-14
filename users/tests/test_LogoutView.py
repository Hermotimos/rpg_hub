from django.test import TestCase
from django.urls import resolve, reverse
from users import views
from users.models import User


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


