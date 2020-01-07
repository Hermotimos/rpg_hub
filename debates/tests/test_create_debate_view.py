from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate, Remark
from debates.forms import CreateDebateForm, CreateRemarkForm
from users.models import User


class CreateDebateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, ])
        self.url = reverse('debates:create-debate', kwargs={'topic_id': self.topic1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('debates:create-debate', kwargs={'topic_id': 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_unallowed(self):
        user2 = User.objects.create_user(username='user2', password='pass1111')
        self.client.force_login(user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        # case request.user.profile in debate1.allowed_profiles
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # case request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/debates/topic:{self.topic1.id}/create-debate/')
        self.assertEquals(view.func, views.create_debate_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form_1(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('debate_form')
        self.assertIsInstance(form, CreateDebateForm)

    def test_contains_form_2(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('remark_form')
        self.assertIsInstance(form, CreateRemarkForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'title': 'Title1',
            'description': 'Description1',
        }
        self.client.post(self.url, data)
        self.assertTrue(Debate.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form2 = response.context.get('debate_form')
        form3 = response.context.get('remark_form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Debate.objects.count() == 2)
        self.assertFalse(Remark.objects.exists())
        self.assertTrue(form2.errors)
        self.assertTrue(form3.errors)

    # TODO Here empty fields given only for topic_form, remark_form has no data. How should this be done?
    # def test_invalid_post_data_empty_fields(self):
    #     self.client.force_login(self.user1)
    #     data = {
    #         'title': '',
    #         'description': '',
    #     }
    #     response = self.client.post(self.url, data)
    #     form1 = response.context.get('debate_form')
    #     form2 = response.context.get('remark_form')
    #     # should show the form again, not redirect
    #     self.assertEquals(response.status_code, 200)
    #     self.assertFalse(Debate.objects.exists())
    #     self.assertFalse(Remark.objects.exists())
    #     self.assertTrue(form1.errors)
    #     self.assertTrue(form2.errors)
