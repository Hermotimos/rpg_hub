from django.test import TestCase
from django.urls import reverse, resolve

from history import views
from history.models import Chapter,  ChronicleEvent, GameSession
from users.models import User


class ChronicleOneChapterTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.status = 'gm'
        self.user4.profile.save()

        self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
        self.game1 = GameSession.objects.create(chapter=self.chapter1, title='Game1')
        self.event1 = ChronicleEvent.objects.create(game=self.game1, event_no_in_game=1)
        self.event1.participants.set([self.user1.profile])
        self.event1.informed.set([self.user2.profile])

        self.url = reverse('history:chronicle-one-chapter', kwargs={'chapter_id': self.chapter1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # request.user.profile neither in event1.informed.all() nor in event1.participants.all(),
        # nor status == 'gm'
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:chronicle-one-chapter', kwargs={'chapter_id': self.chapter1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # request.user.profile in event1.participants.all():
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # request.user.profile in event1.informed.all():
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # request.user.profile.status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/chronicle/one-chapter:{self.chapter1.id}/')
        self.assertEquals(view.func, views.chronicle_one_chapter_view)

    def test_links(self):
        linked_url1 = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})
        linked_url2 = reverse('history:chronicle-note', kwargs={'event_id': self.event1.id})
        linked_url3 = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})

        # request.user.profile in event1.participants.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')

        # request.user.profile in event1.informed.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')

        # request.user.profile.status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
