from django.test import TestCase
from django.urls import reverse, resolve

from characters.models import Character
from knowledge import views
from knowledge.models import KnowledgePacket
from rules.models import Skill
from users.models import User


class AlmanacTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.character1 = Character.objects.create(profile=self.user1.profile)
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.character2 = Character.objects.create(profile=self.user2.profile)
        self.user3 = User.objects.create_user(username='user4', password='pass1111')
        self.character3 = Character.objects.create(profile=self.user3.profile)
        self.user3.profile.status = 'gm'
        self.user3.profile.save()

        self.skill_1 = Skill.objects.create(name='Skill-1')
        self.skill_1.save()
        self.kn_packet_1 = KnowledgePacket.objects.create(title='KnPacket1', text='Text1')
        self.kn_packet_1.skills.set([self.skill_1])
        self.character1.knowledge_packets.set([self.kn_packet_1])

        self.skill_2 = Skill.objects.create(name='Skill-2: Doktryna')
        self.skill_2.save()
        self.kn_packet_2 = KnowledgePacket.objects.create(title='KnPacket2', text='Text2')
        self.kn_packet_2.skills.set([self.skill_2])
        self.character2.knowledge_packets.set([self.kn_packet_2])

        self.url = reverse('knowledge:almanac')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/knowledge/almanac/')
        self.assertEquals(view.func.view_class, views.AlmanacView)

    def test_contains(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'Skill-1')
        self.assertContains(response, 'KnPacket1')
        self.assertNotContains(response, 'Doktryna-1')     # shouldn't contain skill name because skill LIKE 'Doktryn%'
        self.assertNotContains(response, 'KnPacket2')

        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Skill-1')
        self.assertNotContains(response, 'KnPacket1')
        self.assertNotContains(response, 'Doktryna-1')     # shouldn't contain skill name because skill LIKE 'Doktryn%'
        self.assertNotContains(response, 'KnPacket2')

        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, 'Skill-1')
        self.assertContains(response, 'KnPacket1')
        self.assertNotContains(response, 'Doktryna-1')  # shouldn't contain skill name because skill LIKE 'Doktryn%'
        self.assertNotContains(response, 'KnPacket2')
