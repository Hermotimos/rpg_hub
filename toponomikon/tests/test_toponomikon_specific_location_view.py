from django.test import TestCase
from django.urls import reverse, resolve

from imaginarion.models import Picture
from knowledge.models import KnowledgePacketType, KnowledgePacket
from toponomikon import views
from toponomikon.models import GeneralLocation, SpecificLocation
from users.models import User


class ToponomikonSpecificLocationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user1.profile.character_status = 'active_player'
        self.user1.profile.save()

        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'active_player'
        self.user2.profile.save()

        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        pic1 = Picture.objects.create(image='post_pics/topoi_anomeia_MAIN.jpg', type='topoi', title='Title1')

        self.gen_loc_1 = GeneralLocation.objects.create(name='GenLoc1', main_image=pic1)
        self.gen_loc_1.known_directly.set([self.user1.profile])
        self.gen_loc_1.known_indirectly.set([self.user2.profile])

        self.spec_loc_1 = SpecificLocation.objects.create(name='SpecLoc1', general_location=self.gen_loc_1,
                                                          main_image=pic1)
        self.spec_loc_1.known_directly.set([self.user1.profile])
        self.spec_loc_1.known_indirectly.set([self.user2.profile])

        self.kn_packet_type1 = KnowledgePacketType.objects.create(name='Varia')
        self.kn_packet_1 = KnowledgePacket.objects.create(title='KnPacket1', text='Text1')
        self.kn_packet_1.packet_types.set([self.kn_packet_type1])
        self.kn_packet_1.allowed_profiles.set([self.user1.profile])

        self.spec_loc_1.knowledge_packets.set([self.kn_packet_1])

        self.url = reverse('toponomikon:specific-location', kwargs={'spec_loc_id': self.spec_loc_1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('toponomikon:specific-location', kwargs={'spec_loc_id': self.spec_loc_1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # request.user.profile in gen_loc1.known_directly.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        # request.user.profile in gen_loc1.known_indirectly.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/toponomikon/spec-loc:{self.spec_loc_1.id}/')
        self.assertEquals(view.func, views.toponomikon_specific_location_view)

    def test_links(self):
        linked_url1 = reverse('toponomikon:inform', kwargs={'gen_loc_id': 0, 'spec_loc_id': self.spec_loc_1.id})

        # request.user.profile in spec_loc1.known_directly.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')

        # request.user.profile in spec_loc1.known_indirectly.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')

        # request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')

    def test_contains(self):
        # request.user.profile in kn_packet.allowed_profiles.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'KnPacket1')

        # request.user.profile not in kn_packet.allowed_profiles.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'KnPacket1')

        # request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, 'KnPacket1')
