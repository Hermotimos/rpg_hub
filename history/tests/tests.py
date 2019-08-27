from django.test import TestCase
from django.urls import reverse, resolve
from history import views
from history.models import Chapter, GameSession, ChronicleEvent, TimelineEvent, Thread, GeneralLocation, SpecificLocation
from users.models import User


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
        Chapter.objects.create(chapter_no=1, title='Chapter1')

    def test_get(self):
        url = reverse('history:chronicle-one-chapter', kwargs={'chapter_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/one-chapter:1/')
        self.assertEquals(view.func, views.chronicle_one_chapter_view)


class ChronicleOneGameTest(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        ChronicleEvent.objects.create(game_no=game1, event_no_in_game=1, description='Description1')

    def test_get(self):
        url = reverse('history:chronicle-one-game', kwargs={'game_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/one-game:1/')
        self.assertEquals(view.func, views.chronicle_one_game_view)


class ChronicleInformTest(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        ChronicleEvent.objects.create(game_no=game1, event_no_in_game=1, description='Description1')

    def test_get(self):
        url = reverse('history:chronicle-inform', kwargs={'event_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/inform:1/')
        self.assertEquals(view.func, views.chronicle_inform_view)


class ChronicleNoteTest(TestCase):
    def setUp(self):
        gamesession1 = GameSession.objects.create(game_no=1, title='Game1')
        ChronicleEvent.objects.create(game_no=gamesession1, event_no_in_game=1, description='Description1')

    def test_get(self):
        url = reverse('history:chronicle-note', kwargs={'event_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/note:1/')
        self.assertEquals(view.func, views.chronicle_note_view)


class ChronicleEditTest(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        ChronicleEvent.objects.create(game_no=game1, event_no_in_game=1, description='Description1')

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
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        thread1 = Thread.objects.create(name='Thread1')
        event1 = TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1, description='Description1',)
        event1.threads.set([thread1, ])

    def test_get(self):
        url = reverse('history:timeline-thread', kwargs={'thread_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/thread:1/')
        self.assertEquals(view.func, views.timeline_thread_view)


class TimelineParticipantTest(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        user1 = User.objects.create_user(username='user1', password='pass1111')
        event1 = TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1, description='Description1',)
        event1.participants.set([user1.profile, ])

    def test_get(self):
        url = reverse('history:timeline-participant', kwargs={'participant_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/participant:1/')
        self.assertEquals(view.func, views.timeline_participant_view)


class TimelineGeneralLocationtTest(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='genloc1')
        TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1,
                                     description='Description1', general_location=gen_loc1)

    def test_get(self):
        url = reverse('history:timeline-gen-loc', kwargs={'gen_loc_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/gen-loc:1/')
        self.assertEquals(view.func, views.timeline_general_location_view)


class TimelineSpecificLocationtTest(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='genloc1')
        spec_loc1 = SpecificLocation.objects.create(name='specloc1', general_location=gen_loc1)
        event1 = TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1,
                                              description='Description1', general_location=gen_loc1)
        event1.specific_locations.set([spec_loc1, ])

    def test_get(self):
        url = reverse('history:timeline-spec-loc', kwargs={'spec_loc_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/spec-loc:1/')
        self.assertEquals(view.func, views.timeline_specific_location_view)


class TimelineDateTest(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1, description='Description1')

    def test_get(self):
        url_only_year = reverse('history:timeline-date', kwargs={'year': 1, 'season': 0})
        url_year_and_season = reverse('history:timeline-date', kwargs={'year': 1, 'season': 1})
        response_only_year = self.client.get(url_only_year, follow=True)
        response_year_and_season = self.client.get(url_year_and_season, follow=True)
        self.assertEquals(response_only_year.status_code, 200)
        self.assertEquals(response_year_and_season.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/date:1:1/')
        self.assertEquals(view.func, views.timeline_date_view)


class TimelineGameTest(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1, description='Description1')

    def test_get(self):
        url = reverse('history:timeline-game', kwargs={'game_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/game:1/')
        self.assertEquals(view.func, views.timeline_game_view)


class TimelineInformView(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1, description='Description1')

    def test_get(self):
        url = reverse('history:timeline-inform', kwargs={'event_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/inform:1/')
        self.assertEquals(view.func, views.timeline_inform_view)


class TimelineNoteView(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1, description='Description1')

    def test_get(self):
        url = reverse('history:timeline-note', kwargs={'event_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/note:1/')
        self.assertEquals(view.func, views.timeline_note_view)


class TimelineEditView(TestCase):
    def setUp(self):
        game1 = GameSession.objects.create(game_no=1, title='Game1')
        TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1, description='Description1')

    def test_get(self):
        url = reverse('history:timeline-edit', kwargs={'event_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/edit:1/')
        self.assertEquals(view.func, views.timeline_edit_view)
