from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.forms import PasswordChangeForm
from users import views
from users.models import User
from users.forms import UserUpdateForm, UserRegistrationForm, ProfileUpdateForm


class TestLogin(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
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

    def test_csrf(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    # def test_contains_form(self):
    #     response = self.client.get(self.url)
    #     form = response.context.get('form')
    #     self.assertIsInstance(form, XXXXXXXXXXXXX)

    def test_valid_post_data(self):
        data = {
            'username': 'user1',
            'password': 'pass1111',
        }
        self.client.post(self.url, data)
        redirect_url = reverse('users:profile')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        # TODO AttributeError: 'NoneType' object has no attribute 'get'
        #  WHY? This test is copied from:
        #  https://simpleisbetterthancomplex.com/series/2017/09/25/a-complete-beginners-guide-to-django-part-4.html
        # user = response.context.get('user')
        # self.assertTrue(user.is_authenticated)

    def test_invalid_post_data(self):
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # invalid form submission should return to the same page
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        data = {
            'username': '',
            'password': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # invalid form submission should return to the same page
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)


class TestRegister(TestCase):
    def setUp(self):
        self.url = reverse('users:register')
        self.response = self.client.get(self.url)

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/users/register/')
        self.assertEquals(view.func, views.register_view)

    def test_contains_links(self):
        linked_url = reverse('users:login')
        self.assertContains(self.response, f'href="{linked_url}"')

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, UserRegistrationForm)

    def test_valid_post_data(self):
        data = {
            'username': 'user1',
            'email': '',
            'password1': 'pass1111',
            'password2': 'pass1111',
        }
        response = self.client.post(self.url, data)
        redirect_url = reverse('users:login')
        self.assertTrue(User.objects.exists())
        # successful registration should redirect to login url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_invalid_post_data(self):
        data = {}
        response = self.client.post(self.url, data)
        self.assertTrue(User.objects.count() == 0)
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)

    def test_invalid_post_data_empty_fields(self):
        data = {
            'username': '',
            'password': '',
        }
        response = self.client.post(self.url, data)
        self.assertTrue(User.objects.count() == 0)
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)


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

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form_1(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('user_form')
        self.assertIsInstance(form, UserUpdateForm)

    def test_contains_form_2(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('profile_form')
        self.assertIsInstance(form, ProfileUpdateForm)

    # TODO no idea how to test views with 2 forms
    def test_valid_post_data(self):
        pass

    # TODO no idea how to test views with 2 forms
    def test_invalid_post_data(self):
        pass

    # TODO no idea how to test views with 2 forms
    def test_valid_post_data_empty_fields(self):
        pass


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

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, PasswordChangeForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'old_password': 'pass1111',
            'new_password1': '2222newnew',
            'new_password2': '2222newnew',
        }
        old_password = User.objects.get(id=1).password
        response = self.client.post(self.url, data)
        new_password = User.objects.get(id=1).password
        self.assertFalse(old_password == new_password)
        # successful registration should redirect to profile url
        redirect_url = reverse('users:profile')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'old_password': 'wrong_pass',
            'new_password1': '2222newnew',
            'new_password2': '2222newnew',
        }
        old_password = User.objects.get(id=1).password
        response = self.client.post(self.url, data)
        new_password = User.objects.get(id=1).password
        self.assertTrue(old_password == new_password)
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'old_password': '',
            'new_password1': '',
            'new_password2': '',
        }
        old_password = User.objects.get(id=1).password
        response = self.client.post(self.url, data)
        new_password = User.objects.get(id=1).password
        self.assertTrue(old_password == new_password)
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
