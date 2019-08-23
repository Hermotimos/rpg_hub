from django.test import TestCase
from django.urls import reverse, resolve
from history import views
from history.models import GameSession, ChronicleEvent, TimelineEvent, Thread, GeneralLocation, SpecificLocation
from users.models import User
"""
TODO:
timeline_thread_view
timeline_participant_view
timeline_general_location_view
timeline_specific_location_view
timeline_date_view
timeline_game_view
timeline_create_view
timeline_inform_view
timeline_note_view
timeline_edit_view
"""

# ------------------ CHRONICLE ------------------


class ChronicleMainTest(TestCase):
    def test_get(self):
        url = reverse('history:chronicle-main')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/')
        self.assertEquals(view.func, views.chronicle_main_view)


class ChronicleCreateTest(TestCase):
    def test_get(self):
        url = reverse('history:chronicle-create')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/create/')
        self.assertEquals(view.func, views.chronicle_create_view)


class ChronicleAllChaptersTest(TestCase):
    def test_get(self):
        url = reverse('history:chronicle-all-chapters')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/all-chapters/')
        self.assertEquals(view.func, views.chronicle_all_chapters_view)


class ChronicleOneChapterTest(TestCase):
    def setUp(self):
        mock_gamesession = GameSession.objects.create(game_no=1, title='mock_gamesession')
        ChronicleEvent.objects.create(game_no=mock_gamesession, event_no_in_game=1, description='Mock description')

    def test_get(self):
        url = reverse('history:chronicle-one-chapter', kwargs={'game_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/one-chapter:1/')
        self.assertEquals(view.func, views.chronicle_one_chapter_view)


class ChronicleInformTest(TestCase):
    def setUp(self):
        mock_gamesession = GameSession.objects.create(game_no=1, title='mock_gamesession')
        ChronicleEvent.objects.create(game_no=mock_gamesession, event_no_in_game=1, description='Mock description')

    def test_get(self):
        url = reverse('history:chronicle-inform', kwargs={'event_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/inform:1/')
        self.assertEquals(view.func, views.chronicle_inform_view)


class ChronicleNoteTest(TestCase):
    def setUp(self):
        mock_gamesession = GameSession.objects.create(game_no=1, title='mock_gamesession')
        ChronicleEvent.objects.create(game_no=mock_gamesession, event_no_in_game=1, description='Mock description')

    def test_get(self):
        url = reverse('history:chronicle-note', kwargs={'event_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/note:1/')
        self.assertEquals(view.func, views.chronicle_note_view)


class ChronicleEditTest(TestCase):
    def setUp(self):
        mock_gamesession = GameSession.objects.create(game_no=1, title='mock_gamesession')
        ChronicleEvent.objects.create(game_no=mock_gamesession, event_no_in_game=1, description='Mock description')

    def test_get(self):
        url = reverse('history:chronicle-edit', kwargs={'event_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/edit:1/')
        self.assertEquals(view.func, views.chronicle_edit_view)


# ------------------ TIMELINE ------------------


class TimelineMainTest(TestCase):
    def test_get(self):
        url = reverse('history:timeline-main')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/')
        self.assertEquals(view.func, views.timeline_main_view)


class TimelineCreateTest(TestCase):
    def test_get(self):
        url = reverse('history:timeline-create')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/create/')
        self.assertEquals(view.func, views.timeline_create_view)


class TimelineAllEventsTest(TestCase):
    def test_get(self):
        url = reverse('history:timeline-all-events')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/all-events/')
        self.assertEquals(view.func, views.timeline_all_events_view)


class TimelineThreadTest(TestCase):
    def setUp(self):
        mock_gamesession = GameSession.objects.create(game_no=1, title='mock_gamesession')
        mock_thread = Thread.objects.create(name='Mock thread')
        mock_event = TimelineEvent.objects.create(game_no=mock_gamesession, year=1, season=1, day_start=1,
                                                  description='Mock desc',)
        mock_event.threads.set([mock_thread, ])

    def test_get(self):
        url = reverse('history:timeline-thread', kwargs={'thread_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/thread:1/')
        self.assertEquals(view.func, views.timeline_thread_view)


class TimelineParticipantTest(TestCase):
    def setUp(self):
        mock_gamesession = GameSession.objects.create(game_no=1, title='mock_gamesession')
        mock_user = User.objects.create_user(username='Mock_user', password='mockpsswrd111')
        mock_event = TimelineEvent.objects.create(game_no=mock_gamesession, year=1, season=1, day_start=1,
                                                  description='Mock desc',)
        mock_event.participants.set([mock_user.profile, ])

    def test_get(self):
        url = reverse('history:timeline-participant', kwargs={'participant_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/participant:1/')
        self.assertEquals(view.func, views.timeline_participant_view)


class TimelineGeneralLocationtTest(TestCase):
    def setUp(self):
        mock_gamesession = GameSession.objects.create(game_no=1, title='mock_gamesession')
        mock_gen_loc = GeneralLocation.objects.create(name='Mock genloc')
        TimelineEvent.objects.create(game_no=mock_gamesession, year=1, season=1, day_start=1,
                                     description='Mock desc', general_location=mock_gen_loc)

    def test_get(self):
        url = reverse('history:timeline-gen-loc', kwargs={'gen_loc_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/gen-loc:1/')
        self.assertEquals(view.func, views.timeline_general_location_view)


class TimelineSpecificLocationtTest(TestCase):
    def setUp(self):
        mock_gamesession = GameSession.objects.create(game_no=1, title='mock_gamesession')
        mock_gen_loc = GeneralLocation.objects.create(name='Mock genloc')
        mock_spec_loc = SpecificLocation.objects.create(name='Mock specloc', general_location=mock_gen_loc)
        mock_event = TimelineEvent.objects.create(game_no=mock_gamesession, year=1, season=1, day_start=1,
                                                  description='Mock desc', general_location=mock_gen_loc)
        mock_event.specific_locations.set([mock_spec_loc, ])

    def test_get(self):
        url = reverse('history:timeline-spec-loc', kwargs={'spec_loc_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/spec-loc:1/')
        self.assertEquals(view.func, views.timeline_specific_location_view)
