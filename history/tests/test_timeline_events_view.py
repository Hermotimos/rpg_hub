from django.test import TestCase
from django.urls import reverse, resolve

from history import views
from history.models import GameSession, GeneralLocation, SpecificLocation, Thread, TimelineEvent
from imaginarion.models import Picture
from users.models import User


class TimelineEventsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        self.game1 = GameSession.objects.create(title='Game1')
        self.event1 = TimelineEvent.objects.create(game=self.game1, year=1, season=1, day_start=1,
                                                   description='Description1')
        picture1 = Picture.objects.create(image='site_features_pics/img_for_tests.jpg')
        self.gen_loc1 = GeneralLocation.objects.create(name='gen_loc1', main_image=picture1)
        self.spec_loc1 = SpecificLocation.objects.create(name='spec_loc1', general_location=self.gen_loc1,
                                                         main_image=picture1)
        self.thread1 = Thread.objects.create(name='Thread1')

        self.event1.threads.set([self.thread1, ])
        self.event1.general_locations.set([self.gen_loc1, ])
        self.event1.specific_locations.set([self.spec_loc1, ])
        self.participant1 = self.user1
        self.event1.participants.set([self.participant1.profile, ])
        self.event1.informed.set([self.user2.profile, ])

        self.url1 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 0,
                                               'spec_loc_id': 0, 'year': 0, 'season': 0, 'game_id': 0}
        )
        self.url2 = reverse(
            'history:timeline-events', kwargs={'thread_id': 1, 'participant_id': 0, 'gen_loc_id': 0,
                                               'spec_loc_id': 0, 'year': 0, 'season': 0, 'game_id': 0}
        )
        self.url3 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 1, 'gen_loc_id': 0,
                                               'spec_loc_id': 0, 'year': 0, 'season': 0, 'game_id': 0}
        )
        self.url4 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 1,
                                               'spec_loc_id': 0, 'year': 0, 'season': 0, 'game_id': 0}
        )
        self.url5 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 0,
                                               'spec_loc_id': 1, 'year': 0, 'season': 0, 'game_id': 0}
        )
        self.url6 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 0,
                                               'spec_loc_id': 0, 'year': 1, 'season': 0, 'game_id': 0}
        )
        self.url7 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 0,
                                               'spec_loc_id': 0, 'year': 1, 'season': 1, 'game_id': 0}
        )
        self.url8 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 0,
                                              'spec_loc_id': 0, 'year': 0, 'season': 0, 'game_id': 1}
        )

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url1
        response = self.client.get(self.url1)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)

        response = self.client.get(self.url1)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.url2)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.url3)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.url4)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.url5)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.url6)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.url7)
        self.assertEquals(response.status_code, 200)
        response = self.client.get(self.url8)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/thread:0/participant:0/gen-loc:0/spec-loc:0/date:0:0/game:0/')
        self.assertEquals(view.func, views.timeline_filter_events_view)

    def test_links(self):
        linked_url2 = reverse(
            'history:timeline-events', kwargs={'thread_id': self.thread1.id, 'participant_id': 0, 'gen_loc_id': 0,
                                               'spec_loc_id': 0, 'year': 0, 'season': 0, 'game_id': 0}
        )
        linked_url3 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': self.user1.profile.id, 'gen_loc_id': 0,
                                               'spec_loc_id': 0, 'year': 0, 'season': 0, 'game_id': 0}
        )
        linked_url4 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': self.gen_loc1.id,
                                               'spec_loc_id': 0, 'year': 0, 'season': 0, 'game_id': 0}
        )
        linked_url5 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 0,
                                               'spec_loc_id': self.spec_loc1.id, 'year': 0, 'season': 0, 'game_id': 0}
        )
        linked_url6 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 0, 'spec_loc_id': 0,
                                               'year': 1, 'season': 0, 'game_id': 0}
        )
        linked_url7 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 0, 'spec_loc_id': 0,
                                               'year': 1, 'season': 1, 'game_id': 0}
        )
        linked_url8 = reverse(
            'history:timeline-events', kwargs={'thread_id': 0, 'participant_id': 0, 'gen_loc_id': 0, 'spec_loc_id': 0,
                                               'year': 0, 'season': 0, 'game_id': self.game1.id}
        )

        # request.user.profile in event1.participants.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url1)
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')
        self.assertContains(response, f'href="{linked_url8}"')

        # request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url1)
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')
        self.assertContains(response, f'href="{linked_url8}"')

        # request.user.profile neither in event1.participants.all() nor event1.informed.all() - no links
        self.client.force_login(self.user3)
        # follow=True to check on page to which unallowed user is redirected
        response = self.client.get(self.url1, follow=True)
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')
        self.assertNotContains(response, f'href="{linked_url6}"')
        self.assertNotContains(response, f'href="{linked_url7}"')
        self.assertNotContains(response, f'href="{linked_url8}"')

        # request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url1)
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')
        self.assertContains(response, f'href="{linked_url8}"')
