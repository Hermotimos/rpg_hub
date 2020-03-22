from django.test import TestCase
from django.urls import reverse, resolve

from history import views
from history.models import Chapter,  ChronicleEvent, GameSession
from history.forms import ChronicleEventEditForm
from users.models import User
from debates.models import Topic, Debate


class ChronicleEditTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user3.profile.status = 'active_player'
        self.user3.profile.save()
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.status = 'gm'
        self.user4.profile.save()

        self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
        self.game1 = GameSession.objects.create(chapter=self.chapter1, title='Game1')
        self.event1 = ChronicleEvent.objects.create(id=1, game=self.game1, event_no_in_game=1, description='Event1')
        self.event1.participants.set([self.user1.profile])
        self.event1.informed.set([self.user2.profile])
        self.event1.save()

        self.topic1 = Topic.objects.create(title='Topic1')
        self.debate1 = Debate.objects.create(topic=self.topic1, starter=self.user1)

        self.url = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # request.user.profile.status != 'gm'
        self.client.force_login(self.user1)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user4)
        url = reverse('history:chronicle-edit', kwargs={'event_id': self.event1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # request.user.profile.status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/history/chronicle/edit:{self.event1.id}/')
        self.assertEquals(view.func, views.chronicle_edit_view)

    def test_csrf(self):
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, ChronicleEventEditForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user4)
        form = ChronicleEventEditForm(instance=self.event1)
        data = form.initial
        data['description'] = 'changed text'
        data['participants'] = [self.user3.profile.id]
        data['informed'] = [self.user3.profile.id]
        data['debate'] = self.debate1.id
        self.client.post(self.url, data)
        self.assertTrue(ChronicleEvent.objects.get(id=1).description == 'changed text')

    def test_invalid_post_data(self):
        self.client.force_login(self.user4)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user4)
        data = {
            'description': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(ChronicleEvent.objects.get(id=1).description == 'Event1')


#######################################################################################################################
# HINT FOR DEBUGGING FORMS' TESTS:
# If test fails, see list of errors for details. Compare it with data sent.
#     data = {
#         'some_data': 'some_value'
#     }
#     print('DATA:\n', data)
#     response = self.client.post(self.url, data)
#     form1 = response.context.get('form1_name')    # by one form usually form_name is just 'form' - depends how in view
#     form2 = response.context.get('form2_name')
#     print('ERRORS:\n', form1.errors)        # To be run multiple times as only first error in form gets printed
#     print('ERRORS:\n', form2.errors)        # To be run multiple times as only first error in form gets printed
