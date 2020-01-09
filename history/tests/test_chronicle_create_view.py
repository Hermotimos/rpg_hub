from django.test import TestCase
from django.urls import reverse, resolve
from history import views
from history.models import ChronicleEvent, GameSession
from history.forms import ChronicleEventCreateForm
from users.models import User


class ChronicleCreateTest(TestCase):
    def setUp(self):
        self.game1 = GameSession.objects.create(title='Game1')
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'gm'
        self.user2.profile.save()

        self.url = reverse('history:chronicle-create')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # request.user.profile.character_status != 'gm'
        self.client.force_login(self.user1)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        # request.user.profile.character_status == 'gm'
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/create/')
        self.assertEquals(view.func, views.chronicle_create_view)

    def test_csrf(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, ChronicleEventCreateForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user2)
        data = {
            'game': self.game1.id,
            'event_no_in_game': 1,
            'description': 'event1',
        }
        self.assertFalse(ChronicleEvent.objects.exists())
        self.client.post(self.url, data)
        self.assertTrue(ChronicleEvent.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user2)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertFalse(ChronicleEvent.objects.exists())

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user2)
        data = {
            'game': '',
            'event_no_in_game': '',
            'description': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertFalse(ChronicleEvent.objects.exists())


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
