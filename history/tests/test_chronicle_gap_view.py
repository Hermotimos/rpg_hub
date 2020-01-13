from django.test import TestCase
from django.urls import reverse, resolve
from history import views
from history.models import Chapter,  GameSession, TimelineEvent
from users.models import User


class ChronicleGapTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')

        self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
        self.game1 = GameSession.objects.create(chapter=self.chapter1, title='Game1')
        self.timeline_event1 = TimelineEvent.objects.create(game=self.game1, year=1, season=1, day_start=1,
                                                            description='Description1')
        self.timeline_event1.informed.set([self.user1.profile])

        self.url = reverse('history:chronicle-gap', kwargs={'timeline_event_id': self.timeline_event1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/chronicle/gap:{self.timeline_event1.id}/')
        self.assertEquals(view.func, views.chronicle_gap_view)

