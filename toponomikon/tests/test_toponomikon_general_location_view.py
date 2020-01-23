from django.test import TestCase
from django.urls import reverse, resolve

from imaginarion.models import Picture
from toponomikon import views
from toponomikon.models import GeneralLocation, SpecificLocation
from users.models import User


class ToponomikonGeneralLocationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user1.profile.character_status = 'active_player'
        self.user1.profile.save()

        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'active_player'
        self.user2.profile.save()

        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user3.profile.character_status = 'active_player'
        self.user3.profile.save()

        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        pic1 = Picture.objects.create(image='post_pics/topoi_anomeia_MAIN.jpg', type='topoi', title='Title1')

        self.gen_loc_1 = GeneralLocation.objects.create(name='GenLoc1', main_image=pic1)
        self.gen_loc_1.known_directly.set([self.user1.profile])
        self.gen_loc_1.known_indirectly.set([self.user2.profile])

        self.spec_loc_1 = SpecificLocation.objects.create(name='SpecLoc1', general_location=self.gen_loc_1,
                                                          main_image=pic1)
        self.spec_loc_2 = SpecificLocation.objects.create(name='SpecLoc2', general_location=self.gen_loc_1,
                                                          main_image=pic1)
        self.spec_loc_1.known_directly.set([self.user1.profile])
        self.spec_loc_1.known_indirectly.set([self.user2.profile])

        self.url = reverse('toponomikon:general-location', kwargs={'gen_loc_id': self.gen_loc_1.id})

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
        url = reverse('toponomikon:general-location', kwargs={'gen_loc_id': self.gen_loc_1.id + 999})
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
        view = resolve(f'/toponomikon/gen-loc:{self.gen_loc_1.id}/')
        self.assertEquals(view.func, views.toponomikon_general_location_view)

    def test_links(self):
        linked_url1 = reverse('toponomikon:specific-location', kwargs={'spec_loc_id': self.spec_loc_1.id})
        linked_url2 = reverse('toponomikon:specific-location', kwargs={'spec_loc_id': self.spec_loc_2.id})

        # request.user.profile in spec_loc1.known_directly.all()
        # but neither in spec_loc2.known_directly.all() or spec_loc2.known_indirectly.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')

        # request.user.profile in spec_loc1.known_indirectly.all()
        # but neither in spec_loc2.known_directly.all() or spec_loc2.known_indirectly.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')

        # request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
