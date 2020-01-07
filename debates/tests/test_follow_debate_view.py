from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate
from users.models import User


class FollowDebateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.topic1 = Topic.objects.create(title='Topic1')
        self.debate1 = Debate.objects.create(topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, ])
        self.url = reverse('debates:follow', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        user2 = User.objects.create_user(username='user2', password='pass1111')
        self.client.force_login(user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('debates:follow', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed(self):
        self.client.force_login(self.user1)
        redirect_url = reverse('debates:debate', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        # no template generated by follow_debate_view()
        pass

    def test_url_resolves_view(self):
        view = resolve(f'/debates/topic:{self.topic1.id}/debate:{self.debate1.id}/follow/')
        self.assertEquals(view.func, views.follow_debate_view)
