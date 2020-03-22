from django.test import TestCase
from django.urls import reverse, resolve

from rules import views
from rules.models import PlateType
from users.models import User


class RulesTricksTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user3.profile.status = 'gm'
        self.user3.profile.save()

        self.plate1 = PlateType.objects.create(name='Armor1', endurance=10, weight=10, sorting_number=1)
        self.plate1.allowed_profiles.set([self.user1.profile])

        self.url = reverse('rules:tricks')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/rules/tricks/')
        self.assertEquals(view.func, views.rules_tricks_view)

    def test_contains(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'Armor1')

        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Armor1')

        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, 'Armor1')
