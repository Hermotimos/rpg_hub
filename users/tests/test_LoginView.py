from django.test import TestCase
from django.urls import resolve, reverse
from users import views
from users.models import User


class TestLogin(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('users:login')

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/users/login/')
        # for class-based views add .view_class because url ClassBasedView.as_views() creates new function
        self.assertEquals(view.func.view_class, views.LoginView)

    def test_contains_links(self):
        linked_url = reverse('users:register')
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url}"')

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

    def test_invalid_post_data(self):
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        self.assertTrue(form.errors)
        # invalid form submission should return to the same page
        self.assertEquals(response.status_code, 200)

    def test_invalid_post_data_empty_fields(self):
        data = {
            'username': '',
            'password': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        self.assertTrue(form.errors)
        # invalid form submission should return to the same page
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
