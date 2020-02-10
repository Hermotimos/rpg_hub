from django.test import TestCase
from django.urls import reverse, resolve
from characters import views
from characters.models import Character
from users.models import User


class SkillsSheetsForGmTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        Character.objects.create(profile=self.user1.profile)
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        Character.objects.create(profile=self.user2.profile)

        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        self.url = reverse('characters:character-all-skills-for-gm')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # user1.profile.character_ststus != 'gm'
        self.client.force_login(self.user1)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        # user4.profile.character_ststus == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/characters/character-all-skills-for-gm/')
        self.assertEquals(view.func.view_class, views.CharacterAllSkillsForGmView)

    def test_contains(self):
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="/characters/character-skills:{self.user1.profile.id}/"')
        self.assertContains(response, f'href="/characters/character-skills:{self.user2.profile.id}/"')
        # user/profile has no corresponding 'character':
        self.assertNotContains(response, f'href="/characters/character-skills:{self.user3.profile.id}/"')
