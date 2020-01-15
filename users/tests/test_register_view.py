from django.test import TestCase
from django.urls import resolve, reverse
from users import views
from users.models import User
from users.forms import UserRegistrationForm


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
        self.assertFalse(User.objects.exists())
        response = self.client.post(self.url, data)
        redirect_url = reverse('users:login')
        self.assertTrue(User.objects.exists())
        # successful registration should redirect to login url
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_invalid_post_data(self):
        data = {}
        response = self.client.post(self.url, data)
        self.assertFalse(User.objects.exists())
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)

    def test_invalid_post_data_empty_fields(self):
        data = {
            'username': '',
            'password': '',
        }
        response = self.client.post(self.url, data)
        self.assertFalse(User.objects.exists())
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
