from django.test import TestCase
from django.urls import reverse, resolve
from history import views
from history.models import Chapter, ChronicleEvent, GameSession, GeneralLocation, SpecificLocation, Thread, TimelineEvent
from history.forms import TimelineEventCreateForm
from users.models import User


class TimelineCreateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.chapter1 = Chapter.objects.create(chapter_no=1, title='Chapter1')
        self.game1 = GameSession.objects.create(title='Game1')
        self.gen_loc1 = GeneralLocation.objects.create(name='gen_loc1')
        self.spec_loc1 = SpecificLocation.objects.create(name='spec_loc1', general_location=self.gen_loc1)
        self.thread1 = Thread.objects.create(name='Thread1')

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

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, TimelineEventCreateForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'game': self.game1.id,
            'year': 1,
            'season': '1',
            'day_start': 1,
            'day_end': 0,
            'threads': [self.thread1.id, ],
            'description': 'event1',
            'general_location': self.gen_loc1.id,
            'specific_locations': [self.spec_loc1.id, ]
        }
        # response = self.client.post(self.url, data)
        # form = response.context.get('form')
        # print(form.errors)
        self.client.post(self.url, data)
        self.assertTrue(TimelineEvent.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertFalse(ChronicleEvent.objects.exists())
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'game': '',
            'year': '',
            'season': '',
            'day_start': '',
            'threads': '',
            'description': '',
            'general_location': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertFalse(ChronicleEvent.objects.exists())
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
