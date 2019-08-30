from django.test import TestCase
from django.urls import reverse, resolve
from history import views
from history.models import Chapter, GameSession, ChronicleEvent, TimelineEvent, Thread, GeneralLocation, SpecificLocation
from users.models import User


# ------------------ CHRONICLE ------------------


# class ChronicleMainTest(TestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(username='user1', password='pass1111')
#         self.user2 = User.objects.create_user(username='user2', password='pass1111')
#         self.user3 = User.objects.create_user(username='user3', password='pass1111')
#         self.user4 = User.objects.create_user(username='user4', password='pass1111')
#         self.user4.profile.character_status = 'gm'
#
#         self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
#         self.game1 = GameSession.objects.create(id=1, chapter=self.chapter1, title='Game1')
#         self.event1 = ChronicleEvent.objects.create(id=1, game_no=self.game1, event_no_in_game=1, )
#         self.event1.participants.set([self.user1.profile])
#         self.event1.informed.set([self.user2.profile])
#
#         self.url = reverse('history:chronicle-main')
#
#     def test_login_required(self):
#         redirect_url = reverse('users:login') + '?next=' + self.url
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_get(self):
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#     def test_url_resolves_view(self):
#         view = resolve('/history/chronicle/')
#         self.assertEquals(view.func, views.chronicle_main_view)
#
#     def test_contains_links(self):
#         # case request.user.profile in event1.participants.all()
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         linked_url1 = reverse('history:chronicle-all-chapters')
#         linked_url2 = reverse('history:chronicle-one-chapter', kwargs={'chapter_id': self.chapter1.id})
#         linked_url3 = reverse('history:chronicle-one-game', kwargs={'game_id': self.game1.id})
#         self.assertContains(response, f'href="{linked_url1}"')
#         self.assertContains(response, f'href="{linked_url2}"')
#         self.assertContains(response, f'href="{linked_url3}"')
#
#         # case request.user.profile in event1.informed.all()
#         self.client.force_login(self.user2)
#         response = self.client.get(self.url)
#         linked_url1 = reverse('history:chronicle-all-chapters')
#         linked_url2 = reverse('history:chronicle-one-chapter', kwargs={'chapter_id': self.chapter1.id})
#         linked_url3 = reverse('history:chronicle-one-game', kwargs={'game_id': self.game1.id})
#         self.assertContains(response, f'href="{linked_url1}"')
#         self.assertContains(response, f'href="{linked_url2}"')
#         self.assertContains(response, f'href="{linked_url3}"')
#
#         # case doesn't contain links
#         self.client.force_login(self.user3)
#         response = self.client.get(self.url)
#         linked_url2 = reverse('history:chronicle-one-chapter', kwargs={'chapter_id': self.chapter1.id})
#         linked_url3 = reverse('history:chronicle-one-game', kwargs={'game_id': self.game1.id})
#         self.assertNotContains(response, f'href="{linked_url2}"')
#         self.assertNotContains(response, f'href="{linked_url3}"')
#
#         # case request.user.profile.character_status == 'gm'
#         self.client.force_login(self.user4)
#         linked_url2 = reverse('history:chronicle-one-chapter', kwargs={'chapter_id': self.chapter1.id})
#         linked_url3 = reverse('history:chronicle-one-game', kwargs={'game_id': self.game1.id})
#         self.assertNotContains(response, f'href="{linked_url2}"')
#         self.assertNotContains(response, f'href="{linked_url3}"')
#
#
# class ChronicleCreateTest(TestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(username='user1', password='pass1111')
#         self.url = reverse('history:chronicle-create')
#
#     def test_login_required(self):
#         redirect_url = reverse('users:login') + '?next=' + self.url
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_get(self):
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#     def test_url_resolves_view(self):
#         view = resolve('/history/chronicle/create/')
#         self.assertEquals(view.func, views.chronicle_create_view)
#
#
# class ChronicleAllChaptersTest(TestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(username='user1', password='pass1111')
#         self.user2 = User.objects.create_user(username='user2', password='pass1111')
#         self.user3 = User.objects.create_user(username='user3', password='pass1111')
#         self.user4 = User.objects.create_user(username='user4', password='pass1111')
#         self.user4.profile.character_status = 'gm'
#
#         self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
#         self.game1 = GameSession.objects.create(id=1, chapter=self.chapter1, title='Game1')
#         self.event1 = ChronicleEvent.objects.create(id=1, game_no=self.game1, event_no_in_game=1, )
#         self.event1.participants.set([self.user1.profile])
#         self.event1.informed.set([self.user2.profile])
#
#         self.url = reverse('history:chronicle-all-chapters')
#
#     def test_login_required(self):
#         redirect_url = reverse('users:login') + '?next=' + self.url
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_get(self):
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#     def test_url_resolves_view(self):
#         view = resolve('/history/chronicle/all-chapters/')
#         self.assertEquals(view.func, views.chronicle_all_chapters_view)
#
#     def test_contains_links(self):
#         # case request.user.profile in event1.participants.all()
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         self.assertContains(response, f'href="#{self.chapter1.id}"')
#
#         # case request.user.profile in event1.informed.all()
#         self.client.force_login(self.user2)
#         response = self.client.get(self.url)
#         self.assertContains(response, f'href="#{self.chapter1.id}"')
#
#         # case doesn't contain links
#         self.client.force_login(self.user3)
#         response = self.client.get(self.url)
#         self.assertNotContains(response, f'href="#{self.chapter1.id}"')
#
#         # case request.user.profile.character_status == 'gm'
#         self.client.force_login(self.user4)
#         response = self.client.get(self.url)
#         self.assertContains(response, f'href="#{self.chapter1.id}"')
#
#
# class ChronicleOneChapterTest(TestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(username='user1', password='pass1111')
#         self.user2 = User.objects.create_user(username='user2', password='pass1111')
#         self.user3 = User.objects.create_user(username='user3', password='pass1111')
#         self.user4 = User.objects.create_user(username='user4', password='pass1111')
#         self.user4.profile.character_status = 'gm'
#
#         self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
#         self.game1 = GameSession.objects.create(id=1, chapter=self.chapter1, title='Game1')
#         self.event1 = ChronicleEvent.objects.create(id=1, game_no=self.game1, event_no_in_game=1, )
#         self.event1.participants.set([self.user1.profile])
#         self.event1.informed.set([self.user2.profile])
#
#         self.url = reverse('history:chronicle-one-chapter', kwargs={'chapter_id': self.chapter1.id})
#
#     def test_login_required(self):
#         redirect_url = reverse('users:login') + '?next=' + self.url
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_redirect_if_unallowed(self):
#         self.client.force_login(self.user3)
#         redirect_url = reverse('home:dupa')
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_404(self):
#         self.client.force_login(self.user1)
#         url = reverse('history:chronicle-one-chapter', kwargs={'chapter_id': self.chapter1.id + 999})
#         response = self.client.get(url)
#         self.assertEquals(response.status_code, 404)
#
#     def test_get(self):
#         # case: request.user.profile in participants:
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#         # case: request.user.profile in informed:
#         self.client.force_login(self.user2)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#         # case: request.user.profile.character_status == 'gm'
#         self.client.force_login(self.user4)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#     def test_url_resolves_view(self):
#         view = resolve(f'/history/chronicle/one-chapter:{self.chapter1.id}/')
#         self.assertEquals(view.func, views.chronicle_one_chapter_view)
#
#     def test_contains_links(self):
#         # case request.user.profile in event1.participants.all()
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         linked_url1 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url2 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url3 = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})
#         self.assertContains(response, f'href="{linked_url1}"')
#         self.assertContains(response, f'href="{linked_url2}"')
#         self.assertNotContains(response, f'href="{linked_url3}"')
#
#         # case request.user.profile in event1.informed.all()
#         self.client.force_login(self.user2)
#         response = self.client.get(self.url)
#         linked_url1 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url2 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url3 = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})
#         self.assertContains(response, f'href="{linked_url1}"')
#         self.assertContains(response, f'href="{linked_url2}"')
#         self.assertNotContains(response, f'href="{linked_url3}"')
#
#         # case request.user.profile.character_status == 'gm'
#         self.client.force_login(self.user4)
#         response = self.client.get(self.url)
#         linked_url1 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url2 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url3 = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})
#         self.assertContains(response, f'href="{linked_url1}"')
#         self.assertContains(response, f'href="{linked_url2}"')
#         self.assertContains(response, f'href="{linked_url3}"')
#
#
# class ChronicleOneGameTest(TestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(username='user1', password='pass1111')
#         self.user2 = User.objects.create_user(username='user2', password='pass1111')
#         self.user3 = User.objects.create_user(username='user3', password='pass1111')
#         self.user4 = User.objects.create_user(username='user4', password='pass1111')
#         self.user4.profile.character_status = 'gm'
#
#         self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
#         self.game1 = GameSession.objects.create(id=1, chapter=self.chapter1, title='Game1')
#         self.event1 = ChronicleEvent.objects.create(id=1, game_no=self.game1, event_no_in_game=1, )
#         self.event1.participants.set([self.user1.profile])
#         self.event1.informed.set([self.user2.profile])
#
#         self.url = reverse('history:chronicle-one-game', kwargs={'game_id': self.game1.id})
#
#     def test_login_required(self):
#         redirect_url = reverse('users:login') + '?next=' + self.url
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_redirect_if_unallowed(self):
#         self.client.force_login(self.user3)
#         redirect_url = reverse('home:dupa')
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_404(self):
#         self.client.force_login(self.user1)
#         url = reverse('history:chronicle-one-game', kwargs={'game_id': self.game1.id + 999})
#         response = self.client.get(url)
#         self.assertEquals(response.status_code, 404)
#
#     def test_get(self):
#         # case: request.user.profile in participants:
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#         # case: request.user.profile in informed:
#         self.client.force_login(self.user2)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#         # case: request.user.profile.character_status == 'gm'
#         self.client.force_login(self.user4)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#     def test_url_resolves_view(self):
#         view = resolve(f'/history/chronicle/one-game:{self.game1.id}/')
#         self.assertEquals(view.func, views.chronicle_one_game_view)
#
#     def test_contains_links(self):
#         # case request.user.profile in event1.participants.all()
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         linked_url1 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url2 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url3 = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})
#         self.assertContains(response, f'href="{linked_url1}"')
#         self.assertContains(response, f'href="{linked_url2}"')
#         self.assertNotContains(response, f'href="{linked_url3}"')
#
#         # case request.user.profile in event1.informed.all()
#         self.client.force_login(self.user2)
#         response = self.client.get(self.url)
#         linked_url1 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url2 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url3 = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})
#         self.assertContains(response, f'href="{linked_url1}"')
#         self.assertContains(response, f'href="{linked_url2}"')
#         self.assertNotContains(response, f'href="{linked_url3}"')
#
#         # case request.user.profile.character_status == 'gm'
#         self.client.force_login(self.user4)
#         response = self.client.get(self.url)
#         linked_url1 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url2 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#         linked_url3 = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})
#         self.assertContains(response, f'href="{linked_url1}"')
#         self.assertContains(response, f'href="{linked_url2}"')
#         self.assertContains(response, f'href="{linked_url3}"')
#
#
# class ChronicleInformTest(TestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(username='user1', password='pass1111')
#         self.user2 = User.objects.create_user(username='user2', password='pass1111')
#         self.user3 = User.objects.create_user(username='user3', password='pass1111')
#         self.user4 = User.objects.create_user(username='user4', password='pass1111')
#         self.user4.profile.character_status = 'gm'
#
#         self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
#         self.game1 = GameSession.objects.create(id=1, chapter=self.chapter1, title='Game1')
#         self.event1 = ChronicleEvent.objects.create(id=1, game_no=self.game1, event_no_in_game=1, )
#         self.event1.participants.set([self.user1.profile])
#         self.event1.informed.set([self.user2.profile])
#
#         self.url = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
#
#     def test_login_required(self):
#         redirect_url = reverse('users:login') + '?next=' + self.url
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_redirect_if_unallowed(self):
#         self.client.force_login(self.user3)
#         redirect_url = reverse('home:dupa')
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_404(self):
#         self.client.force_login(self.user1)
#         url = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id + 999})
#         response = self.client.get(url)
#         self.assertEquals(response.status_code, 404)
#
#     def test_get(self):
#         # case: request.user.profile in participants:
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#         # case: request.user.profile in informed:
#         self.client.force_login(self.user2)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#         # case: request.user.profile.character_status == 'gm'
#         self.client.force_login(self.user4)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#     def test_url_resolves_view(self):
#         view = resolve('/history/chronicle/inform:1/')
#         self.assertEquals(view.func, views.chronicle_inform_view)
#
#
# class ChronicleNoteTest(TestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(username='user1', password='pass1111')
#         self.user2 = User.objects.create_user(username='user2', password='pass1111')
#         self.user3 = User.objects.create_user(username='user3', password='pass1111')
#         self.user4 = User.objects.create_user(username='user4', password='pass1111')
#         self.user4.profile.character_status = 'gm'
#
#         self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
#         self.game1 = GameSession.objects.create(id=1, chapter=self.chapter1, title='Game1')
#         self.event1 = ChronicleEvent.objects.create(id=1, game_no=self.game1, event_no_in_game=1, )
#         self.event1.participants.set([self.user1.profile])
#         self.event1.informed.set([self.user2.profile])
#
#         self.url = reverse('history:chronicle-note', kwargs={'event_id': self.event1.id})
#
#     def test_login_required(self):
#         redirect_url = reverse('users:login') + '?next=' + self.url
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_redirect_if_unallowed(self):
#         self.client.force_login(self.user3)
#         redirect_url = reverse('home:dupa')
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_404(self):
#         self.client.force_login(self.user1)
#         url = reverse('history:chronicle-note', kwargs={'event_id': self.event1.id + 999})
#         response = self.client.get(url)
#         self.assertEquals(response.status_code, 404)
#
#     def test_get(self):
#         # case: request.user.profile in participants:
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#         # case: request.user.profile in informed:
#         self.client.force_login(self.user2)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#         # case: request.user.profile.character_status == 'gm'
#         self.client.force_login(self.user4)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#     def test_url_resolves_view(self):
#         view = resolve(f'/history/chronicle/note:{self.event1.id}/')
#         self.assertEquals(view.func, views.chronicle_note_view)
#
#
# class ChronicleEditTest(TestCase):
#     def setUp(self):
#         self.user1 = User.objects.create_user(username='user1', password='pass1111')
#         self.user1.profile.character_status = 'gm'
#         self.user2 = User.objects.create_user(username='user2', password='pass1111')
#
#         self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
#         self.game1 = GameSession.objects.create(id=1, chapter=self.chapter1, title='Game1')
#         self.event1 = ChronicleEvent.objects.create(id=1, game_no=self.game1, event_no_in_game=1, )
#         self.event1.participants.set([self.user2.profile])
#         self.event1.informed.set([self.user2.profile])
#
#         self.url = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})
#
#     def test_login_required(self):
#         redirect_url = reverse('users:login') + '?next=' + self.url
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_redirect_if_unallowed(self):
#         # case: request.user.profile.character_status != 'gm'
#         self.client.force_login(self.user2)
#         redirect_url = reverse('home:dupa')
#         response = self.client.get(self.url)
#         self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
#
#     def test_404(self):
#         self.client.force_login(self.user1)
#         url = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id + 999})
#         response = self.client.get(url)
#         self.assertEquals(response.status_code, 404)
#
#     def test_get(self):
#         # case: request.user.profile.character_status == 'gm'
#         self.client.force_login(self.user1)
#         response = self.client.get(self.url)
#         self.assertEquals(response.status_code, 200)
#
#     def test_url_resolves_view(self):
#         view = resolve(f'/history/chronicle/edit:{self.event1.id}/')
#         self.assertEquals(view.func, views.chronicle_edit_view)
#

# # ------------------ TIMELINE ------------------


class TimelineMainTest(TestCase):
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
        self.event1 = TimelineEvent.objects.create(game_no=self.game1, year=1, season=1, day_start=1,
                                                   description='Description1', general_location=self.gen_loc1)
        self.event1.threads.set([self.thread1, ])
        self.event1.specific_locations.set([self.spec_loc1, ])
        self.participant1 = self.user1
        self.event1.participants.set([self.participant1.profile, ])
        self.event1.informed.set([self.user2.profile, ])

        self.url = reverse('history:timeline-main')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/')
        self.assertEquals(view.func, views.timeline_main_view)

    def test_links(self):
        # case request.user.profile in event1.participants.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        linked_url1 = reverse('history:timeline-all-events')
        linked_url2 = reverse('history:timeline-thread', kwargs={'thread_id': self.thread1.id})
        linked_url3 = reverse('history:timeline-participant', kwargs={'participant_id': self.participant1.id})
        linked_url4 = reverse('history:timeline-gen-loc', kwargs={'gen_loc_id': self.gen_loc1.id})
        linked_url5 = reverse('history:timeline-spec-loc', kwargs={'spec_loc_id': self.spec_loc1.id})
        linked_url6 = reverse('history:timeline-date', kwargs={'year': 1, 'season': 1})
        linked_url7 = reverse('history:timeline-game', kwargs={'game_id': self.game1.id})
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')

        # case request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        linked_url1 = reverse('history:timeline-all-events')
        linked_url2 = reverse('history:timeline-thread', kwargs={'thread_id': self.thread1.id})
        linked_url3 = reverse('history:timeline-participant', kwargs={'participant_id': self.participant1.id})
        linked_url4 = reverse('history:timeline-gen-loc', kwargs={'gen_loc_id': self.gen_loc1.id})
        linked_url5 = reverse('history:timeline-spec-loc', kwargs={'spec_loc_id': self.spec_loc1.id})
        linked_url6 = reverse('history:timeline-date', kwargs={'year': 1, 'season': 1})
        linked_url7 = reverse('history:timeline-game', kwargs={'game_id': self.game1.id})
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')

        # case doesn't contain links
        # for request.user.profile neither in event1.participants.all() nor event1.informed.all()
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        linked_url2 = reverse('history:timeline-thread', kwargs={'thread_id': self.thread1.id})
        linked_url3 = reverse('history:timeline-participant', kwargs={'participant_id': self.participant1.id})
        linked_url4 = reverse('history:timeline-gen-loc', kwargs={'gen_loc_id': self.gen_loc1.id})
        linked_url5 = reverse('history:timeline-spec-loc', kwargs={'spec_loc_id': self.spec_loc1.id})
        linked_url6 = reverse('history:timeline-date', kwargs={'year': 1, 'season': 1})
        linked_url7 = reverse('history:timeline-game', kwargs={'game_id': self.game1.id})
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')
        self.assertNotContains(response, f'href="{linked_url6}"')
        self.assertNotContains(response, f'href="{linked_url7}"')

        # case request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        linked_url1 = reverse('history:timeline-all-events')
        linked_url2 = reverse('history:timeline-thread', kwargs={'thread_id': self.thread1.id})
        linked_url3 = reverse('history:timeline-participant', kwargs={'participant_id': self.participant1.id})
        linked_url4 = reverse('history:timeline-gen-loc', kwargs={'gen_loc_id': self.gen_loc1.id})
        linked_url5 = reverse('history:timeline-spec-loc', kwargs={'spec_loc_id': self.spec_loc1.id})
        linked_url6 = reverse('history:timeline-date', kwargs={'year': 1, 'season': 1})
        linked_url7 = reverse('history:timeline-game', kwargs={'game_id': self.game1.id})
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')
        self.assertContains(response, f'href="{linked_url6}"')
        self.assertContains(response, f'href="{linked_url7}"')


class TimelineCreateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('history:timeline-create')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/timeline/create/')
        self.assertEquals(view.func, views.timeline_create_view)


class TimelineAllEventsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
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


class TimelineThreadTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        game1 = GameSession.objects.create(title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        self.thread1 = Thread.objects.create(name='Thread1')
        event1 = TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1,
                                              description='Description1', general_location=gen_loc1)
        event1.threads.set([self.thread1, ])
        event1.participants.set([self.user1.profile, ])
        event1.informed.set([self.user2.profile, ])

        self.url = reverse('history:timeline-thread', kwargs={'thread_id': self.thread1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:timeline-thread', kwargs={'thread_id': self.thread1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # case: request.user.profile in event1.participant.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/timeline/thread:{self.thread1.id}/')
        self.assertEquals(view.func, views.timeline_thread_view)


class TimelineParticipantTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')

        game1 = GameSession.objects.create(title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        self.event1 = TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1,
                                                   description='Description1', general_location=gen_loc1)
        self.event1.participants.set([self.user1.profile, self.user4.profile])
        self.event1.informed.set([self.user2.profile, ])

        self.url = reverse('history:timeline-participant', kwargs={'participant_id': self.user4.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:timeline-thread', kwargs={'thread_id': self.user4.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # case: request.user.profile in event1.participant.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile in event1.participant.all() and is the searched participant
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/timeline/participant:{self.user4.id}/')
        self.assertEquals(view.func, views.timeline_participant_view)


class TimelineGeneralLocationtTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        game1 = GameSession.objects.create(title='Game1')
        self.gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        event1 = TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1,
                                              description='Description1', general_location=self.gen_loc1)
        event1.participants.set([self.user1.profile, ])
        event1.informed.set([self.user2.profile, ])

        self.url = reverse('history:timeline-gen-loc', kwargs={'gen_loc_id': self.gen_loc1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:timeline-gen-loc', kwargs={'gen_loc_id': self.gen_loc1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # case: request.user.profile in event1.participant.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/timeline/gen-loc:{self.gen_loc1.id}/')
        self.assertEquals(view.func, views.timeline_general_location_view)


class TimelineSpecificLocationtTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        game1 = GameSession.objects.create(title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        self.spec_loc1 = SpecificLocation.objects.create(name='spec_loc1', general_location=gen_loc1)
        event1 = TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1,
                                              description='Description1', general_location=gen_loc1)
        event1.participants.set([self.user1.profile, ])
        event1.informed.set([self.user2.profile, ])
        event1.specific_locations.set([self.spec_loc1, ])

        self.url = reverse('history:timeline-spec-loc', kwargs={'spec_loc_id': 1})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:timeline-spec-loc', kwargs={'spec_loc_id': self.spec_loc1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # case: request.user.profile in event1.participant.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/timeline/spec-loc:{self.spec_loc1.id}/')
        self.assertEquals(view.func, views.timeline_specific_location_view)


class TimelineDateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        game1 = GameSession.objects.create(title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        event1 = TimelineEvent.objects.create(game_no=game1, year=1, season=1, day_start=1,
                                              description='Description1', general_location=gen_loc1)
        event1.participants.set([self.user1.profile, ])
        event1.informed.set([self.user2.profile, ])

        self.url_only_year = reverse('history:timeline-date', kwargs={'year': 1, 'season': 0})
        self.url_year_and_season = reverse('history:timeline-date', kwargs={'year': 1, 'season': 1})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url_only_year
        response = self.client.get(self.url_only_year)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url_only_year)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # no test_404() becaues no objects timeline_date_view() has no args and calls no object with get_object_or_404()

    def test_get(self):
        # case: request.user.profile in event1.participant.all()
        self.client.force_login(self.user1)
        response_only_year = self.client.get(self.url_only_year)
        response_year_and_season = self.client.get(self.url_year_and_season)
        self.assertEquals(response_only_year.status_code, 200)
        self.assertEquals(response_year_and_season.status_code, 200)

        # case: request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response_only_year = self.client.get(self.url_only_year)
        response_year_and_season = self.client.get(self.url_year_and_season)
        self.assertEquals(response_only_year.status_code, 200)
        self.assertEquals(response_year_and_season.status_code, 200)

    def test_url_resolves_view(self):
        view_only_year = resolve('/history/timeline/date:1:0/')
        view_year_and_season = resolve('/history/timeline/date:1:1/')
        self.assertEquals(view_only_year.func, views.timeline_date_view)
        self.assertEquals(view_year_and_season.func, views.timeline_date_view)


class TimelineGameTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        self.game1 = GameSession.objects.create(title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        event1 = TimelineEvent.objects.create(game_no=self.game1, year=1, season=1, day_start=1,
                                              description='Description1', general_location=gen_loc1)
        event1.participants.set([self.user1.profile, ])
        event1.informed.set([self.user2.profile, ])

        self.url = reverse('history:timeline-game', kwargs={'game_id': self.game1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:timeline-game', kwargs={'game_id': self.game1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # case: request.user.profile in event1.participant.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/timeline/game:{self.game1.id}/')
        self.assertEquals(view.func, views.timeline_game_view)


class TimelineInformView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        self.game1 = GameSession.objects.create(title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        self.event1 = TimelineEvent.objects.create(game_no=self.game1, year=1, season=1, day_start=1,
                                                   description='Description1', general_location=gen_loc1)
        self.event1.participants.set([self.user1.profile, ])
        self.event1.informed.set([self.user2.profile, ])

        self.url = reverse('history:timeline-inform', kwargs={'event_id': self.event1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:timeline-inform', kwargs={'event_id': self.event1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # case: request.user.profile in event1.participant.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/timeline/inform:{self.event1.id}/')
        self.assertEquals(view.func, views.timeline_inform_view)


class TimelineNoteView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')

        self.game1 = GameSession.objects.create(title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        self.event1 = TimelineEvent.objects.create(game_no=self.game1, year=1, season=1, day_start=1,
                                                   description='Description1', general_location=gen_loc1)
        self.event1.participants.set([self.user1.profile, ])
        self.event1.informed.set([self.user2.profile, ])

        self.url = reverse('history:timeline-note', kwargs={'event_id': self.event1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:timeline-note', kwargs={'event_id': self.event1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # case: request.user.profile in event1.participant.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case: request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/timeline/note:{self.event1.id}/')
        self.assertEquals(view.func, views.timeline_note_view)


class TimelineEditView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')

        self.user4.profile.character_status = 'gm'
        self.game1 = GameSession.objects.create(title='Game1')
        gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        self.event1 = TimelineEvent.objects.create(game_no=self.game1, year=1, season=1, day_start=1,
                                                   description='Description1', general_location=gen_loc1)
        self.event1.participants.set([self.user1.profile, ])
        self.event1.informed.set([self.user2.profile, ])

        self.url = reverse('history:timeline-edit', kwargs={'event_id': self.event1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        redirect_url = reverse('home:dupa')

        # case: request.user.profile in event1.participant.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        # case: request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        # case: request.user.profile neither in event1.participant.all() nor in event1.informed.all()
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:timeline-edit', kwargs={'event_id': self.event1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # case: request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/timeline/edit:{self.event1.id}/')
        self.assertEquals(view.func, views.timeline_edit_view)
