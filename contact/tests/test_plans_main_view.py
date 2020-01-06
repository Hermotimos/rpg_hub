from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Plan
from users.models import User


class PlansMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.plan1 = Plan.objects.create(author=self.user1)
        self.url = reverse('contact:plans-main')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/plans/main/')
        self.assertEquals(view.func, views.plans_main_view)

    def test_links(self):
        linked_url1 = reverse('contact:plans-create')
        linked_url2 = reverse('contact:plans-modify', kwargs={'plan_id': self.plan1.id})
        linked_url3 = reverse('contact:plans-delete', kwargs={'plan_id': self.plan1.id})

        # request.user is author
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')

        # request.user is not author
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')
