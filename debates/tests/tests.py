from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate
from users.models import User


class DebatesMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, name='Debate1', topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, ])
        self.url = reverse('debates:main')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/')
        self.assertEquals(view.func, views.debates_main_view)

    def test_links(self):
        linked_url1 = reverse('debates:create-topic')
        linked_url2 = reverse('debates:create-debate', kwargs={'topic_id': self.topic1.id})
        linked_url3 = reverse('debates:debate', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})

        # case request.user.profile  in debate1.allowed_profiles
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')

        # case request.user.profile not in debate1.allowed_profiles
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')


class CreateTopicTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('debates:create-topic')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/create_topic/')
        self.assertEquals(view.func, views.create_topic_view)


class CreateDebateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, ])
        self.url = reverse('debates:create-debate', kwargs={'topic_id': self.topic1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

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
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/debates/topic:{self.topic1.id}/create-debate/')
        self.assertEquals(view.func, views.create_debate_view)


class DebateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, self.user2.profile, ])
        self.debate1.followers.set([self.user1.profile, ])
        self.url = reverse('debates:debate', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_redirect_if_unallowed(self):
        user3 = User.objects.create_user(username='user3', password='pass1111')
        self.client.force_login(user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('debates:debate', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user1)
        self.response = self.client.get(self.url)
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/debates/topic:{self.topic1.id}/debate:{self.debate1.id}/')
        self.assertEquals(view.func, views.debate_view)

    def test_links(self):
        linked_url1 = reverse('debates:invite', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})
        linked_url2 = reverse('debates:unfollow', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})
        linked_url3 = reverse('debates:follow', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})

        # case request.user.profile in debate1.followers
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')

        # case request.user.profile not in debate1.followers
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')


class DebatesInviteTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, ])
        self.url = reverse('debates:invite', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_redirect_if_unallowed(self):
        user2 = User.objects.create_user(username='user2', password='pass1111')
        self.client.force_login(user2)
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


class UnfollowDebateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, ])
        self.url = reverse('debates:unfollow', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})

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

    # No test_get - no template generated by unfollow_debate_view()

    def test_url_resolves_view(self):
        view = resolve(f'/debates/topic:{self.topic1.id}/debate:{self.debate1.id}/unfollow/')
        self.assertEquals(view.func, views.unfollow_debate_view)


class FollowDebateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, topic=self.topic1, starter=self.user1)
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

    # No test_get - no template generated by follow_debate_view()

    def test_url_resolves_view(self):
        view = resolve(f'/debates/topic:{self.topic1.id}/debate:{self.debate1.id}/follow/')
        self.assertEquals(view.func, views.follow_debate_view)
