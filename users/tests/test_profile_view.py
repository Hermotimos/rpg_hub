from django.test import TestCase
from django.urls import resolve, reverse
from users import views
from users.models import User
from users.forms import UserUpdateForm, ProfileUpdateForm


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

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        form1 = UserUpdateForm(instance=self.user1)
        form2 = ProfileUpdateForm(instance=self.user1.profile)
        data1 = form1.initial
        data2 = form2.initial

        data1.update(data2)
        data1['username'] = 'Changed_name'
        data1['email'] = 'mock_email@new.com'
        data1['character_name'] = 'New character name'

        self.assertTrue(self.user1.username == 'user1')
        self.assertTrue(self.user1.email == '')
        self.assertTrue(self.user1.profile.character_name == 'user1')

        self.client.post(self.url, data1)
        response = self.client.get(self.url)

        self.assertContains(response, 'Changed_name')
        self.assertContains(response, 'mock_email@new.com')
        self.assertContains(response, 'New character name')
        # or
        self.assertEqual(response.context['user_form'].initial['username'], 'Changed_name')
        self.assertEqual(response.context['user_form'].initial['email'], 'mock_email@new.com')
        self.assertEqual(response.context['profile_form'].initial['character_name'], 'New character name')

        # TODO: these fail, why?
        # self.assertTrue(self.user1.username == 'Changed_name')
        # self.assertTrue(self.user1.email == 'mock_email@new.com')
        # self.assertTrue(self.user1.profile.character_name == 'New character name')

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}

        self.assertTrue(self.user1.username == 'user1')
        self.assertTrue(self.user1.email == '')
        self.assertTrue(self.user1.profile.character_name == 'user1')

        self.client.post(self.url, data)
        response = self.client.get(self.url)

        self.assertNotContains(response, 'Changed_name')
        self.assertNotContains(response, 'mock_email@new.com')
        self.assertNotContains(response, 'New character name')
        # or
        self.assertNotEqual(response.context['user_form'].initial['username'], 'Changed_name')
        self.assertNotEqual(response.context['user_form'].initial['email'], 'mock_email@new.com')
        self.assertNotEqual(response.context['profile_form'].initial['character_name'], 'New character name')

    def test_valid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        form1 = UserUpdateForm(instance=self.user1)
        form2 = ProfileUpdateForm(instance=self.user1.profile)
        data1 = form1.initial
        data2 = form2.initial

        data1.update(data2)
        data1['username'] = ''
        data1['email'] = ''
        data1['character_name'] = ''

        self.assertTrue(self.user1.username == 'user1')
        self.assertTrue(self.user1.email == '')
        self.assertTrue(self.user1.profile.character_name == 'user1')

        self.client.post(self.url, data1)
        response = self.client.get(self.url)

        self.assertNotContains(response, 'Changed_name')
        self.assertNotContains(response, 'mock_email@new.com')
        self.assertNotContains(response, 'New character name')
        # or
        self.assertNotEqual(response.context['user_form'].initial['username'], 'Changed_name')
        self.assertNotEqual(response.context['user_form'].initial['email'], 'mock_email@new.com')
        self.assertNotEqual(response.context['profile_form'].initial['character_name'], 'New character name')


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
