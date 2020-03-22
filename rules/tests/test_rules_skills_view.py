from django.test import TestCase
from django.urls import reverse, resolve

from rules import views
from rules.models import Skill, SkillLevel, Synergy, SynergyLevel
from users.models import User


class RulesSkillsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user3.profile.status = 'gm'
        self.user3.profile.save()

        self.skill_1 = Skill.objects.create(name='Skill-1', tested_trait='ZRC')
        self.skill_2 = Skill.objects.create(name='Skill-2', tested_trait='ZRC')
        self.skill_1.allowed_profiles.set([self.user1.profile, self.user2.profile])
        self.skill_2.allowed_profiles.set([self.user1.profile])

        self.skill_1_lvl_1 = SkillLevel.objects.create(skill=self.skill_1, level='0', description='Desc-Skill-1-Lvl-1')

        self.synergy_1 = Synergy.objects.create(id=1, name='Skill-1 + Skill-2')
        self.synergy_1.skills.set([self.skill_1, self.skill_2])
        self.synergy_1.allowed_profiles.set([self.user1.profile])

        self.synergy_1_lvl_1 = SynergyLevel.objects.create(synergy=self.synergy_1, level='1',
                                                           description='Desc-Syn-1-Lvl-1')

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

    def test_contains(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'Skill-1')
        self.assertContains(response, 'Desc-Skill-1-Lvl-1')
        self.assertContains(response, 'Skill-2')
        self.assertContains(response, 'Skill-1 + Skill-2')
        self.assertContains(response, 'Desc-Syn-1-Lvl-1')

        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, 'Skill-1')
        self.assertContains(response, 'Desc-Skill-1-Lvl-1')
        self.assertNotContains(response, 'Skill-2')
        self.assertNotContains(response, 'Skill-1 + Skill-2')
        self.assertNotContains(response, 'Desc-Syn-1-Lvl-1')

        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, 'Skill-1')
        self.assertContains(response, 'Desc-Skill-1-Lvl-1')
        self.assertContains(response, 'Skill-2')
        self.assertContains(response, 'Skill-1 + Skill-2')
        self.assertContains(response, 'Desc-Syn-1-Lvl-1')
