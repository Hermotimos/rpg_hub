from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand
from contact.forms import DemandsCreateForm
from users.models import User


class DemandsCreateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='u1', password='ps1')
        self.user2 = User.objects.create_user(username='u2', password='ps1')
        self.user1.profile.status = 'active_player'
        self.user2.profile.status = 'active_player'
        self.user1.profile.save()
        self.user2.profile.save()
        
        self.url = reverse('contact:demands-create')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302,
                             target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/create/')
        self.assertEquals(view.func, views.demands_create_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, DemandsCreateForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'addressee': self.user2.id,  # by ForeignKeyField pk or id required
            'text': 'Demand2',
        }
        self.assertFalse(Demand.objects.exists())
        self.client.post(self.url, data)
        self.assertTrue(Demand.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertFalse(Demand.objects.exists())

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'addressee': '',
            'text': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertFalse(Demand.objects.exists())


###############################################################################
# HINT FOR DEBUGGING FORMS' TESTS:
# If test fails, see list of errors for details. Compare it with data sent.
#     data = {
#         'some_data': 'some_value'
#     }
#     print('DATA:\n', data)
#     response = self.client.post(self.url, data)
#     # by one form usually form_name is just 'form' - depends how in view
#     form1 = response.context.get('form1_name')
#     form2 = response.context.get('form2_name')
#     # To be run multiple times as only first error in form gets printed:
#     print('ERRORS:\n', form1.errors)
#     print('ERRORS:\n', form2.errors)
