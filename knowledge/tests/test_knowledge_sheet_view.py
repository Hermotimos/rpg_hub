from django.test import TestCase
from django.urls import reverse, resolve

from characters.models import Character
from knowledge import views
from knowledge.models import KnowledgePacketType, KnowledgePacket
from rules.models import Skill, SkillLevel
from users.models import User


class KnowledgeSheetTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.character1 = Character.objects.create(profile=self.user1.profile)
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.character2 = Character.objects.create(profile=self.user2.profile)

        self.user3 = User.objects.create_user(username='user4', password='pass1111')
        self.user3.profile.character_status = 'gm'
        self.user3.profile.save()

        self.kn_packet_type1 = KnowledgePacketType.objects.create(name='Varia')
        self.kn_packet_1 = KnowledgePacket.objects.create(title='KnPacket1', text='Text1')
        self.kn_packet_1.packet_types.set([self.kn_packet_type1])
        self.kn_packet_1.allowed_profiles.set([self.user1.profile])

        self.kn_packet_type2 = KnowledgePacketType.objects.create(name='Teologia')
        self.kn_packet_2 = KnowledgePacket.objects.create(title='KnPacket2', text='Text2')
        self.kn_packet_2.packet_types.set([self.kn_packet_type2])
        self.kn_packet_2.allowed_profiles.set([self.user2.profile])

        self.skill_1 = Skill.objects.create(name='Skill-1')
        self.skill_1.save()
        self.skill_1_lvl_1 = SkillLevel.objects.create(skill=self.skill_1, level='1')
        self.skill_1_lvl_2 = SkillLevel.objects.create(skill=self.skill_1, level='2')

        self.skill_2 = Skill.objects.create(name='Doktryna-1')
        self.skill_2.save()
        self.skill_2_lvl_1 = SkillLevel.objects.create(skill=self.skill_2, level='1')
        self.skill_2_lvl_2 = SkillLevel.objects.create(skill=self.skill_2, level='2')

        self.skill_2_lvl_2.knowledge_packets.set([self.kn_packet_2])

        self.character1.skill_levels_acquired.set([self.skill_1_lvl_1, self.skill_1_lvl_2])
        self.character2.skill_levels_acquired.set([self.skill_2_lvl_1, self.skill_2_lvl_2])

        self.url = reverse('knowledge:knowledge-sheet')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/knowledge/knowledge-sheet/')
        self.assertEquals(view.func, views.knowledge_sheet_view)

    def test_contains(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'Varia')
        self.assertNotContains(response, 'Teologia')
        self.assertContains(response, 'KnPacket1')
        self.assertNotContains(response, 'Skill-1')     # shouldn't contain skill name unless packet type == 'Teologia'

        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, 'Teologia')
        self.assertNotContains(response, 'Varia')
        self.assertContains(response, 'KnPacket2')
        self.assertContains(response, 'Doktryna-1')     # should contain skill name because packet type == 'Teologia'

        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, 'Varia')
        self.assertContains(response, 'Teologia')
        self.assertContains(response, 'KnPacket1')
        self.assertContains(response, 'KnPacket2')
        self.assertNotContains(response, 'Skill-1')     # shouldn't contain skill name unless packet type == 'Teologia'
        self.assertContains(response, 'Doktryna-1')     # should contain skill name because packet type == 'Teologia'
