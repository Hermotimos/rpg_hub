from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.forms import PasswordChangeForm
from users import views
from users.models import User


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


#######################################################################################################################
# HINT FOR DEBUGGING FORMS' TESTS:
# If test fails, see list of errors for details. Compare it with data sent.
#     data = {
#         'some_data': 'some_value'
#     }
#     print('DATA:\n', data)
#     response = self.client.post(self.url, data)
#     form1 = response.context.get('form1_name')    # by one form usually form_name is just 'form' - depends how in view
#     form2 = response.context.get('form2_name')
#     print('ERRORS:\n', form1.errors)        # To be run multiple times as only first error in form gets printed
#     print('ERRORS:\n', form2.errors)        # To be run multiple times as only first error in form gets printed
