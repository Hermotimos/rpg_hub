from django.test import TestCase
from django.urls import reverse, resolve
from history import views
from history.models import GameSession, GeneralLocation, SpecificLocation, Thread, TimelineEvent
from users.models import User


class TimelineAllEventsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'

        self.game1 = GameSession.objects.create(title='Game1')
        self.gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        self.spec_loc1 = SpecificLocation.objects.create(name='spec_loc1', general_location=self.gen_loc1)
        self.thread1 = Thread.objects.create(name='Thread1')
        self.event1 = TimelineEvent.objects.create(game=self.game1, year=1, season=1, day_start=1,
                                                   description='Description1', general_location=self.gen_loc1)
        self.event1.threads.set([self.thread1, ])
        self.event1.specific_locations.set([self.spec_loc1, ])
        self.participant1 = self.user1
        self.event1.participants.set([self.participant1.profile, ])
        self.event1.informed.set([self.user2.profile, ])

        self.url = reverse('history:timeline-all-events')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/all-events/')
        self.assertEquals(view.func, views.timeline_all_events_view)

    def test_links(self):
        linked_url2 = reverse('history:timeline-thread', kwargs={'thread_id': self.thread1.id})
        linked_url3 = reverse('history:timeline-participant', kwargs={'participant_id': self.participant1.id})
        linked_url4 = reverse('history:timeline-gen-loc', kwargs={'gen_loc_id': self.gen_loc1.id})
        linked_url5 = reverse('history:timeline-spec-loc', kwargs={'spec_loc_id': self.spec_loc1.id})
        linked_url6 = reverse('history:timeline-date', kwargs={'year': 1, 'season': 0})     # case only year specified
        linked_url7 = reverse('history:timeline-date', kwargs={'year': 1, 'season': 1})
        linked_url8 = reverse('history:timeline-game', kwargs={'game_id': self.game1.id})

        # case request.user.profile in event1.participants.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')
        self.assertContains(response, f'href="{linked_url8}"')

        # case request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')
        self.assertContains(response, f'href="{linked_url8}"')

        # case request.user.profile neither in event1.participants.all() nor event1.informed.all() - no links
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')
        self.assertNotContains(response, f'href="{linked_url6}"')
        self.assertNotContains(response, f'href="{linked_url7}"')
        self.assertNotContains(response, f'href="{linked_url8}"')

        # case request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')
        self.assertContains(response, f'href="{linked_url8}"')
