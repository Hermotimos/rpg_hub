from django.test import TestCase
from django.urls import reverse, resolve

from rules import views
from rules.models import CharacterClass, CharacterProfession, EliteClass, EliteProfession
from users.models import User


class RulesProfessionsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user3.profile.status = 'gm'
        self.user3.profile.save()

        self.class1 = CharacterClass.objects.create(name='Class1')
        self.profession1 = CharacterProfession.objects.create(name='Profession1', character_class=self.class1)
        self.profession1.allowed_profiles.set([self.user1.profile])

        self.elite_class1 = EliteClass.objects.create(name='EliteClass1')
        self.elite_class1.allowed_profiles.set([self.user1.profile])
        self.elite_profession1 = EliteProfession.objects.create(name='EliteProfession1',  elite_class=self.elite_class1)
        self.elite_profession1.allowed_profiles.set([self.user1.profile])

        self.url = reverse('rules:professions')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/rules/professions/')
        self.assertEquals(view.func, views.rules_professions_view)

    def test_contains(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'Class1')
        self.assertContains(response, 'Profession1')
        self.assertContains(response, 'EliteClass1')
        self.assertContains(response, 'EliteProfession1')

        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Class1')
        self.assertNotContains(response, 'Profession1')
        self.assertNotContains(response, 'EliteClass1')
        self.assertNotContains(response, 'EliteProfession1')

        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, 'Class1')
        self.assertContains(response, 'Profession1')
        self.assertContains(response, 'EliteClass1')
        self.assertContains(response, 'EliteProfession1')
