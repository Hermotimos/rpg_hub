from django.test import TestCase
from django.urls import reverse, resolve
from characters import views
from users.models import User


class TricksViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user1.profile.character_status = 'active_player'
        self.user1.profile.character_name = 'ProfileName1'
        self.user1.profile.save()

        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'inactive_player'
        self.user2.profile.character_name = 'ProfileName2'
        self.user2.profile.save()

        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user3.profile.character_status = 'dead_player'
        self.user3.profile.character_name = 'ProfileName3'
        self.user3.profile.save()

        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        self.url = reverse('characters:tricks')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/characters/tricks/')
        self.assertEquals(view.func.view_class, views.CharacterTricksView)

    def test_contains(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'ProfileName1')
        self.assertNotContains(response, 'ProfileName2')

        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertNotContains(response, 'ProfileName1')
        self.assertNotContains(response, 'ProfileName2')

        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, 'ProfileName1')
        self.assertContains(response, 'ProfileName2')
        self.assertNotContains(response, 'ProfileName3')   # shouldn't contain profile.character_status == 'dead_player'
