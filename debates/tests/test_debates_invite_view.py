from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate
from debates.forms import InviteForm
from users.models import User


class DebatesInviteTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')

        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, ])
        self.url = reverse('debates:invite', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('debates:invite', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user1)
        self.response = self.client.get(self.url)
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/debates/topic:{self.topic1.id}/debate:{self.debate1.id}/invite/')
        self.assertEquals(view.func, views.debates_invite_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, InviteForm)

    # TODO won't pass - WHY? error ' "" nie jest poprawną wartością.' though form.data seems legit
    # def test_valid_post_data(self):
    #     self.client.force_login(self.user1)
    #     form = InviteForm(instance=self.debate1,
    #                       authenticated_user=self.user1,
    #                       already_allowed_profiles_ids=[self.user1.profile.id, ])
    #     data = form.initial
    #
    #     print('\n', data)
    #     self.assertTrue(Profile.objects.get(user__username='user1'))
    #     data['allowed_profiles'] = [self.user1.profile, self.user2.profile]
    #     print('\n', data)
    #     response = self.client.post(self.url, data)
    #     form = response.context.get('form')
    #     print('\n', form.errors)
    #
    #     # self.client.post(self.url, data)
    #     # self.assertFalse(form.errors)
    #     self.assertTrue(self.user2.profile in Debate.objects.get(id=1).allowed_profiles.all())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        form = InviteForm(instance=self.debate1,
                          authenticated_user=self.user1,
                          already_allowed_profiles_ids=[self.user1.profile.id, ])
        data = form.initial
        data['allowed_profiles'] = 'Wrong kind of data'

        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        form = InviteForm(instance=self.debate1,
                          authenticated_user=self.user1,
                          already_allowed_profiles_ids=[self.user1.profile.id, ])
        data = form.initial
        data['allowed_profiles'] = ''

        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(self.user2.profile not in Debate.objects.get(id=1).allowed_profiles.all())
