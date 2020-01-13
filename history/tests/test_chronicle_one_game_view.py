from django.test import TestCase
from django.urls import reverse, resolve

from history import views
from history.models import Chapter,  ChronicleEvent, GameSession, TimelineEvent
from users.models import User


class ChronicleOneGameTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()
        self.user5 = User.objects.create_user(username='user5', password='pass1111')

        self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
        self.game1 = GameSession.objects.create(chapter=self.chapter1, title='Game1')
        self.event1 = ChronicleEvent.objects.create(game=self.game1, event_no_in_game=1)
        self.event1.participants.set([self.user1.profile])
        self.event1.informed.set([self.user2.profile])

        self.timeline_event1 = TimelineEvent.objects.create(game=self.game1, year=1, season=1, day_start=1,
                                                            description='Description1')
        self.timeline_event1.informed.set([self.user5.profile])

        self.url = reverse('history:chronicle-one-game', kwargs={'game_id': self.game1.id, 'timeline_event_id': 0})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # case request.user.profile neither in event1.informed.all() nor in event1.participants.all(),
        # nor character_status == 'gm'
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_specific(self):
        # request.user.profile uses 'history:chronicle-one-game' via timeline_main.html
        # where user is informed about TimelineEvent, but isn't allowed to the corresponding ChronicleEvent's game
        self.client.force_login(self.user5)
        url = reverse('history:chronicle-one-game', kwargs={'game_id': self.game1.id,
                                                            'timeline_event_id': self.timeline_event1.id})
        redirect_url = reverse('history:chronicle-gap', kwargs={'timeline_event_id': self.timeline_event1.id})
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:chronicle-one-game', kwargs={'game_id': self.game1.id + 999, 'timeline_event_id': 0})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # case: request.user.profile in event1.participants.all():
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile in event1.informed.all():
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/chronicle/one-game:{self.game1.id}:{0}/')
        self.assertEquals(view.func, views.chronicle_one_game_view)

    def test_links(self):
        linked_url1 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
        linked_url2 = reverse('history:chronicle-note', kwargs={'event_id': self.event1.id})
        linked_url3 = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})

        # case request.user.profile in event1.participants.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')

        # case request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')

        # case request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')


# TODO test with timeline_event and timeline_even_id from it as second kwarg