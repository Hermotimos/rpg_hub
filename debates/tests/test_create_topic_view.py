from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate, Remark
from debates.forms import CreateTopicForm, CreateDebateForm, CreateRemarkForm
from users.models import User


class CreateTopicTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('debates:create-topic')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/create_topic/')
        self.assertEquals(view.func, views.create_topic_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form_1(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('topic_form')
        self.assertIsInstance(form, CreateTopicForm)

    def test_contains_form_2(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('debate_form')
        self.assertIsInstance(form, CreateDebateForm)

    def test_contains_form_3(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('remark_form')
        self.assertIsInstance(form, CreateRemarkForm)

    # TODO view with 3 forms - no idea how to test it
    # def test_valid_post_data(self):
    #     self.client.force_login(self.user1)
    #     data = {
    #         # Topic
    #         'title': 'Title1',
    #         'description': 'Description1',
    #         # TODO should data for other forms go here???
    #     }
    #     self.client.post(self.url, data)
    #     self.assertTrue(Topic.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form1 = response.context.get('topic_form')
        form2 = response.context.get('debate_form')
        form3 = response.context.get('remark_form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Debate.objects.exists())
        self.assertFalse(Remark.objects.exists())
        self.assertTrue(form1.errors)
        self.assertTrue(form2.errors)
        self.assertTrue(form3.errors)

    # TODO Here empty fields given only for topic_form, other forms have no data. How should this be done?
    # def test_invalid_post_data_empty_fields(self):
    #     self.client.force_login(self.user1)
    #     data = {
    #         'title': '',
    #         'description': '',
    #     }
    #     response = self.client.post(self.url, data)
    #     form1 = response.context.get('topic_form')
    #     form2 = response.context.get('debate_form')
    #     form3 = response.context.get('remark_form')
    #     # should show the form again, not redirect
    #     self.assertEquals(response.status_code, 200)
    #     self.assertFalse(Topic.objects.exists())
    #     self.assertFalse(Debate.objects.exists())
    #     self.assertFalse(Remark.objects.exists())
    #     self.assertTrue(form1.errors)
    #     self.assertTrue(form2.errors)
    #     self.assertTrue(form3.errors)


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
