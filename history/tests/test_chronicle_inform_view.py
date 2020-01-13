from django.test import TestCase
from django.urls import reverse, resolve

from history import views
from history.models import Chapter,  ChronicleEvent, GameSession
from history.forms import ChronicleEventInformForm
from users.models import User


class ChronicleInformTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user3.profile.character_status = 'active_player'
        self.user3.profile.save()
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
        self.game1 = GameSession.objects.create(chapter=self.chapter1, title='Game1')
        self.event1 = ChronicleEvent.objects.create(id=1, game=self.game1, event_no_in_game=1)
        self.event1.participants.set([self.user1.profile])
        self.event1.informed.set([self.user2.profile])

        self.url = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # request.user.profile neither in event1.informed.all() nor in event1.participants.all(),
        # nor character_status == 'gm'
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('history:chronicle-inform', kwargs={'event_id': self.event1.id + 999})
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

        # request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/history/chronicle/inform:1/')
        self.assertEquals(view.func, views.chronicle_inform_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, ChronicleEventInformForm)

    def test_valid_post_data1(self):
        # participant user1 informs an uninformed user3
        self.client.force_login(self.user1)
        form = ChronicleEventInformForm(authenticated_user=self.user1,
                                        old_informed=[self.user2.profile.id, ],
                                        participants=[self.user1.profile.id, ],
                                        instance=self.event1)
        data = form.initial
        data['informed'] = [self.user3.profile.id]
        self.assertFalse(self.user3.profile in ChronicleEvent.objects.get(id=1).informed.all())
        self.client.post(self.url, data)
        self.assertTrue(self.user3.profile in ChronicleEvent.objects.get(id=1).informed.all())

    def test_valid_post_data2(self):
        # informed user2 informs an uninformed user3
        self.client.force_login(self.user2)
        form = ChronicleEventInformForm(authenticated_user=self.user1,
                                        old_informed=[self.user2.profile.id, ],
                                        participants=[self.user1.profile.id, ],
                                        instance=self.event1)
        data = form.initial
        data['informed'] = [self.user3.profile.id]
        self.assertFalse(self.user3.profile in ChronicleEvent.objects.get(id=1).informed.all())
        self.client.post(self.url, data)
        self.assertTrue(self.user3.profile in ChronicleEvent.objects.get(id=1).informed.all())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        form = ChronicleEventInformForm(authenticated_user=self.user1,
                                        old_informed=[self.user2.profile.id, ],
                                        participants=[self.user1.profile.id, ],
                                        instance=self.event1)
        data = form.initial
        data['informed'] = 'Invalid data'
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        form = ChronicleEventInformForm(authenticated_user=self.user1,
                                        old_informed=[self.user2.profile.id, ],
                                        participants=[self.user1.profile.id, ],
                                        instance=self.event1)
        data = form.initial
        data['informed'] = ''
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)


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
