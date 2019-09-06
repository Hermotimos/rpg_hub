from django.test import TestCase
from django.urls import reverse, resolve
from rules import views
from rules.models import Skill, Synergy
from users.models import User


class RulesMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('rules:main')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/rules/')
        self.assertEquals(view.func, views.rules_main_view)


class RulesSkillsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.skill1 = Skill.objects.create(name='Skill1', tested_trait='ZRC', )
        self.skill2 = Skill.objects.create(name='Skill2', tested_trait='ZRC', )
        self.synergy1 = Synergy.objects.create()
        self.synergy1.skills.set([self.skill1, self.skill2])
        self.skill1.allowed_profiles.set([self.user1.profile])
        self.synergy1.allowed_profiles.set([self.user1.profile])

        self.url = reverse('rules:skills')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/rules/skills/')
        self.assertEquals(view.func, views.rules_skills_view)

    def test_contains_content(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'Skill1')
        self.assertContains(response, 'Skill1 + Skill2')

    def test_not_contains_content(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Skill1')
        self.assertNotContains(response, 'Skill1 + Skill2')


class RulesCombatTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('rules:combat')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/rules/combat/')
        self.assertEquals(view.func, views.rules_combat_view)
