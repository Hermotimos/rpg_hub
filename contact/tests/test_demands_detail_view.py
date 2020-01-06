from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand,  DemandAnswer
from contact.forms import DemandAnswerForm
from users.models import User


class DemandsDetailTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.demand1 = Demand.objects.create(author=self.user1, addressee=self.user2, text='Demand1')
        self.url = reverse('contact:demands-detail', kwargs={'demand_id': self.demand1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # request.user is neither author nor addressee - cannot view details
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('contact:demands-detail', kwargs={'demand_id': self.demand1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get_1(self):
        # request.user is author
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_get_2(self):
        # request.user is addressee
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/contact/demands/detail:{self.demand1.id}/')
        self.assertEquals(view.func, views.demands_detail_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, DemandAnswerForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'text': 'Answer text',
        }
        self.assertFalse(DemandAnswer.objects.exists())
        self.client.post(self.url, data)
        self.assertTrue(DemandAnswer.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'text': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertFalse(DemandAnswer.objects.exists())
