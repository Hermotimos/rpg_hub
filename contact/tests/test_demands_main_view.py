from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand
from users.models import User


class DemandsMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.demand1 = Demand.objects.create(author=self.user1, addressee=self.user2, text='Demand1')
        self.demand2 = Demand.objects.create(author=self.user1, addressee=self.user2, text='Demand2', is_done=True)
        self.url = reverse('contact:demands-main')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/main/')
        self.assertEquals(view.func, views.demands_main_view)

    def test_links(self):
        linked_url1 = reverse('contact:demands-create')
        # demand1.is_done=False
        linked_url2 = reverse('contact:done', kwargs={'demand_id': self.demand1.id})
        linked_url3 = reverse('contact:undone', kwargs={'demand_id': self.demand1.id})
        linked_url4 = reverse('contact:demands-delete', kwargs={'demand_id': self.demand1.id})
        # demand2.is_done=True
        linked_url5 = reverse('contact:done', kwargs={'demand_id': self.demand2.id})
        linked_url6 = reverse('contact:undone', kwargs={'demand_id': self.demand2.id})
        linked_url7 = reverse('contact:demands-delete', kwargs={'demand_id': self.demand2.id})

        # request.user is author
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')

        # request.user is addressee
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertNotContains(response, f'href="{linked_url7}"')

        # request.user is neither author nor addressee
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')
        self.assertNotContains(response, f'href="{linked_url6}"')
        self.assertNotContains(response, f'href="{linked_url7}"')
