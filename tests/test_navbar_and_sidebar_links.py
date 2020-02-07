from django.test import TestCase
from django.urls import reverse

from characters.models import Character
from users.models import User


class TestNavbarAndSidebarLinks(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'gm'
        self.user2.profile.save()

        self.character1 = Character.objects.create(profile=self.user1.profile)
        self.client.force_login(self.user1)
        self.url = reverse('home:home')
        self.response = self.client.get(self.url)

    def test_contains_navbar_and_sidebar_links(self):
        # NAVBAR - for non-gm users:
        self.assertContains(self.response, f'href="{reverse("home:home")}"')
        self.assertContains(self.response, f'href="{reverse("news:main")}"')
        self.assertContains(self.response, f'href="{reverse("contact:demands-main")}"')
        self.assertContains(self.response, f'href="{reverse("rules:main")}"')
        self.assertContains(self.response, f'href="{reverse("history:timeline-main")}"')
        self.assertContains(self.response, f'href="{reverse("history:chronicle-main")}"')
        self.assertContains(self.response, f'href="{reverse("debates:main")}"')
        self.assertContains(self.response, f'href="{reverse("toponomikon:main")}"')
        self.assertContains(self.response,
                            f'href="{reverse("characters:skills-sheet", kwargs={"profile_id": "0"})}"')
        self.assertContains(self.response, f'href="{reverse("knowledge:knowledge-sheet")}"')
        self.assertContains(self.response, f'href="{reverse("characters:tricks")}"')
        self.assertContains(self.response, f'href="{reverse("contact:plans-main")}"')
        self.assertContains(self.response, f'href="{reverse("contact:demands-create")}"')
        self.assertContains(self.response, f'href="{reverse("users:logout")}"')

        # SIDEBAR - for all users:
        self.assertContains(self.response, f'href="{reverse("users:profile")}"')

        # logging in 'gm' user
        self.client.force_login(self.user2)
        response = self.client.get(self.url)

        # NAVBAR - for gm users:
        self.assertContains(response, f'href="{reverse("characters:skills-sheets-for-gm")}"')
        self.assertContains(response, f'href="{reverse("contact:plans-for-gm")}"')

        # SIDEBAR - for game-master users:
        self.assertContains(response, f'href="{reverse("admin:index")}"')
        self.assertContains(response, f'href="{reverse("history:chronicle-create")}"')
        self.assertContains(response, f'href="{reverse("history:timeline-create")}"')

        # SIDEBAR - for visitor users:
        # no such character_status at the moment
