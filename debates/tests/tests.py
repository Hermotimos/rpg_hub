from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate
from users.models import User


class DebatesMainTest(TestCase):
    def setUp(self):
        # user1  - create, log in
        user1 = User.objects.create_user(username='user1', password='pass1111')
        self.client.force_login(user1)

    def test_login_required(self):
        self.client.logout()
        url = reverse('debates:main')
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        url = reverse('debates:main')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/')
        self.assertEquals(view.func, views.debates_main_view)


class CreateTopicTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='pass1111')
        self.client.force_login(user1)

    def test_login_required(self):
        self.client.logout()
        url = reverse('debates:create-topic')
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        url = reverse('debates:create-topic')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/create_topic/')
        self.assertEquals(view.func, views.create_topic_view)


class CreateDebateTest(TestCase):
    def setUp(self):
        # user1  - create, log in and add to Debate.allowed_profiles
        user1 = User.objects.create_user(username='user1', password='pass1111')
        self.client.force_login(user1)
        topic1 = Topic.objects.create(id=1)
        debate1 = Debate.objects.create(id=1, topic=topic1, starter=user1)
        debate1.allowed_profiles.set([user1.profile, ])
        # testing if user1 is added to allowed
        # self.assertTrue(self.user1.profile in self.debate1.allowed_profiles.all())
        # self.assertTrue(self.user1.profile in self.topic1.allowed_list())

    def test_login_required(self):
        self.client.logout()
        url = reverse('debates:create-debate', kwargs={'topic_id': 1})
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        url = reverse('debates:create-debate', kwargs={'topic_id': 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_unallowed(self):
        user2 = User.objects.create_user(username='user2', password='pass1111')
        self.client.force_login(user2)
        url = reverse('debates:create-debate', kwargs={'topic_id': 1})
        redirect_url = reverse('home:dupa')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        url = reverse('debates:create-debate', kwargs={'topic_id': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/create-debate/')
        self.assertEquals(view.func, views.create_debate_view)

    # ensures other test don't base on objects created in this one: variables in setUp have to begin with 'self. '
    # def clean_up(self):
    #     self.user1.delete()
    #     self.t1opic.delete()
    #     self.debate1.delete()
    #     self.assertFalse(User.objects.all())
    #     self.assertFalse(Topic.objects.all())
    #     self.assertFalse(Debate.objects.all())


class DebateTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='pass1111')
        self.client.force_login(user1)
        topic1 = Topic.objects.create(id=1, title='Topic1', description='Description1')
        debate1 = Debate.objects.create(id=1, topic=topic1, starter=user1)
        debate1.allowed_profiles.set([user1.profile, ])

    def test_login_required(self):
        self.client.logout()
        url = reverse('debates:debate', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        user2 = User.objects.create_user(username='user2', password='pass1111')
        self.client.force_login(user2)
        url = reverse('debates:debate', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('home:dupa')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        url = reverse('debates:debate', kwargs={'topic_id': 1, 'debate_id': 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        url = reverse('debates:debate', kwargs={'topic_id': 1, 'debate_id': 1})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/debate:1/')
        self.assertEquals(view.func, views.debate_view)


class DebatesInviteTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='pass1111')
        self.client.force_login(user1)
        topic1 = Topic.objects.create(id=1, title='Topic1', description='Description1')
        debate1 = Debate.objects.create(id=1, topic=topic1, starter=user1)
        debate1.allowed_profiles.set([user1.profile, ])

    def test_login_required(self):
        self.client.logout()
        url = reverse('debates:invite', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        user2 = User.objects.create_user(username='user2', password='pass1111')
        self.client.force_login(user2)
        url = reverse('debates:invite', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('home:dupa')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        url = reverse('debates:invite', kwargs={'topic_id': 1, 'debate_id': 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        url = reverse('debates:invite', kwargs={'topic_id': 1, 'debate_id': 1})
        self.response = self.client.get(url)
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/debate:1/invite/')
        self.assertEquals(view.func, views.debates_invite_view)


class UnfollowDebateTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='pass1111')
        self.client.force_login(user1)
        topic1 = Topic.objects.create(id=1, title='Topic1', description='Description1')
        debate1 = Debate.objects.create(id=1, topic=topic1, starter=user1)
        debate1.allowed_profiles.set([user1.profile, ])

    def test_login_required(self):
        self.client.logout()
        url = reverse('debates:unfollow', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        user2 = User.objects.create_user(username='user2', password='pass1111')
        self.client.force_login(user2)
        url = reverse('debates:unfollow', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('home:dupa')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        url = reverse('debates:unfollow', kwargs={'topic_id': 1, 'debate_id': 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed(self):
        url = reverse('debates:unfollow', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('debates:debate', kwargs={'topic_id': 1, 'debate_id': 1})
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/debate:1/unfollow/')
        self.assertEquals(view.func, views.unfollow_debate_view)

    # No test_get - no template generated by unfollow_debate_view()


class FollowDebateTest(TestCase):
    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='pass1111')
        self.client.force_login(user1)
        topic1 = Topic.objects.create(id=1, title='Topic1', description='Description1')
        debate1 = Debate.objects.create(id=1, topic=topic1, starter=user1)
        debate1.allowed_profiles.set([user1.profile, ])

    def test_login_required(self):
        self.client.logout()
        url = reverse('debates:follow', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        user2 = User.objects.create_user(username='user2', password='pass1111')
        self.client.force_login(user2)
        url = reverse('debates:follow', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('home:dupa')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        url = reverse('debates:follow', kwargs={'topic_id': 1, 'debate_id': 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed(self):
        url = reverse('debates:follow', kwargs={'topic_id': 1, 'debate_id': 1})
        redirect_url = reverse('debates:debate', kwargs={'topic_id': 1, 'debate_id': 1})
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/debate:1/follow/')
        self.assertEquals(view.func, views.follow_debate_view)

    # No test_get - no template generated by follow_debate_view()
