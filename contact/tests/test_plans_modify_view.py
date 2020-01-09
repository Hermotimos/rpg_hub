from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand, Plan, DemandAnswer
from contact.forms import DemandsCreateForm, DemandAnswerForm, PlansCreateForm, PlansModifyForm
from users.models import User


class PlansModifyTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.plan1 = Plan.objects.create(author=self.user1, text='Plan1')
        self.url = reverse('contact:plans-modify', kwargs={'plan_id': self.plan1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # only authors are allowed to modify plans
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('contact:plans-modify', kwargs={'plan_id': self.plan1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/contact/plans/modify:{self.plan1.id}/')
        self.assertEquals(view.func, views.plans_modify_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, PlansModifyForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        form = PlansModifyForm(instance=self.plan1)
        data = form.initial
        data['text'] = 'changed text'
        data['image'] = ''      # Necessary, otherwise ValueError: The 'image' attribute has no file associated with it.
        self.client.post(self.url, data)
        self.assertTrue(self.plan1.text == 'changed text')

    def test_invalid_post_data(self):
        # There is no possibility to provide invalid data apart from providing empty 'text' field (next test)
        pass

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        form = PlansModifyForm(instance=self.plan1)
        data = form.initial
        data['text'] = ''
        data['image'] = ''      # Necessary, otherwise ValueError: The 'image' attribute has no file associated with it.
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(self.plan1.text == 'Plan1')


#######################################################################################################################
# HINT FOR DEBUGGING FORMS' TESTS:
# If test fails, see list of errors for details. Compare it with data sent.
#     data = {
#         'some_data': 'some_value'
#     }
#     print('DATA:\n', data)
#     response = self.client.post(self.url, data)
#     form = response.context.get('form_name')    # usually form_name is just 'form'
#     print('ERRORS:\n', form_name.errors)        # To be run multiple times as only first error in form gets printed
