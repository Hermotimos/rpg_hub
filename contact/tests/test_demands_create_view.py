from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand
from contact.forms import DemandsCreateForm
from users.models import User


class DemandsCreateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'active_player'
        self.user2.save()
        self.url = reverse('contact:demands-create')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

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

    # ---IMPORTANT NOTE---
    # Manual test - OK. Tests fails when there's a custom queryset for 'addressee' field in the form.
    # When the form is left without custom queryset for 'addressee' field, the test passes.
    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'addressee': '2',     # by ForeignKeyField pk or id has to be provided
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
