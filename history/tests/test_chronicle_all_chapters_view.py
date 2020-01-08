from django.test import TestCase
from django.urls import reverse, resolve
from history import views
from history.models import Chapter,  ChronicleEvent, GameSession
from users.models import User


class ChronicleAllChaptersTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
        self.game1 = GameSession.objects.create(id=1, chapter=self.chapter1, title='Game1')
        self.event1 = ChronicleEvent.objects.create(id=1, game=self.game1, event_no_in_game=1, )
        self.event1.participants.set([self.user1.profile])
        self.event1.informed.set([self.user2.profile])

        self.url = reverse('history:chronicle-all-chapters')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/all-chapters/')
        self.assertEquals(view.func, views.chronicle_all_chapters_view)

    def test_links(self):
        # case request.user.profile in event1.participants.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="#{self.chapter1.id}"')

        # case request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="#{self.chapter1.id}"')

        # case request.user.profile neither in informed nor in participants nor character_status == 'gm'
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertNotContains(response, f'href="#{self.chapter1.id}"')

        # case request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="#{self.chapter1.id}"')
