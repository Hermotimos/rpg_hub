from django.test import TestCase
from django.urls import reverse, resolve

from characters import views
from characters.models import Character
from rules.models import Skill, SkillLevel, Synergy, SynergyLevel
from users.models import User


class SkillsSheetTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.character1 = Character.objects.create(profile=self.user1.profile)
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.character2 = Character.objects.create(profile=self.user2.profile)

        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        self.skill_1 = Skill.objects.create(name='Skill-1')
        self.skill_1.save()
        self.skill_1_lvl_1 = SkillLevel.objects.create(skill=self.skill_1, level='1')
        self.skill_1_lvl_2 = SkillLevel.objects.create(skill=self.skill_1, level='2')

        self.skill_2 = Skill.objects.create(name='Skill-2')
        self.skill_2.save()
        self.skill_2_lvl_1 = SkillLevel.objects.create(skill=self.skill_2, level='1')
        self.skill_2_lvl_2 = SkillLevel.objects.create(skill=self.skill_2, level='2')

        self.synergy1 = Synergy(id=1, name='Synergy1')
        self.synergy1.save()
        self.synergy1.skills.set([self.skill_1, self.skill_2])
        self.synergy1_lvl_1 = SynergyLevel.objects.create(synergy=self.synergy1, level='1')

        self.character1.skill_levels_acquired.set([self.skill_1_lvl_1, self.skill_1_lvl_2, self.skill_2_lvl_1])
        self.character1.synergy_levels_acquired.set([self.synergy1_lvl_1])
        self.character2.skill_levels_acquired.set([self.skill_2_lvl_1, self.skill_2_lvl_2])

        # user's own skills sheet:
        self.url_1 = reverse('characters:character-skills', kwargs={'profile_id': '0'})
        # skills sheet of specific user:
        self.url_2 = reverse('characters:character-skills', kwargs={'profile_id': '2'})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url_1
        response = self.client.get(self.url_1)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user1)
        redirect_url = reverse('home:dupa')
        # another user's skills sheet (url_2):
        response = self.client.get(self.url_2)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        # user's own skills sheet (url_1):
        self.client.force_login(self.user1)
        response = self.client.get(self.url_1)
        self.assertEquals(response.status_code, 200)

        # another user's skills sheet (url_2) accessible for user4.profile.character_status == 'gm':
        self.client.force_login(self.user4)
        response = self.client.get(self.url_2)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/characters/skills-sheets-for-gm/')
        self.assertEquals(view.func, views.skills_sheets_for_gm_view)

    def test_contains(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url_1)
        self.assertNotContains(response, f'{self.skill_1.name} [1]')
        self.assertContains(response, f'{self.skill_1.name} [2]')
        self.assertContains(response, f'{self.skill_2.name} [1]')
        self.assertNotContains(response, f'{self.skill_2.name} [2]')
        self.assertContains(response, f'{self.synergy1.name} [1]')

        self.client.force_login(self.user2)
        response = self.client.get(self.url_1)
        self.assertNotContains(response, f'{self.skill_1.name} [1]')
        self.assertNotContains(response, f'{self.skill_1.name} [2]')
        self.assertNotContains(response, f'{self.skill_2.name} [1]')
        self.assertContains(response, f'{self.skill_2.name} [2]')
        self.assertNotContains(response, f'{self.synergy1.name} [1]')
