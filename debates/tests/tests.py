from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate
from users.models import User


class DebatesMainTest(TestCase):
    def test_get(self):
        url = reverse('debates:main')
        response = self.client.get(url, follow=True)            # follow=True follows beyond @login_required
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/')
        self.assertEquals(view.func, views.debates_main_view)


class CreateTopicTest(TestCase):
    def test_get(self):
        url = reverse('debates:create-topic')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/create_topic/')
        self.assertEquals(view.func, views.create_topic_view)


class CreateDebateTest(TestCase):
    def setUp(self):
        Topic.objects.create(title='Mock Topic', description='Mock description.')

    def test_get(self):
        url = reverse('debates:create-debate', kwargs={'topic_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    # 404 not testable with @login_required because redirection to login page returns 200 success code
    # def test_404(self):
    #     url = reverse('debates:create-debate', kwargs={'topic_id': 100})
    #     response = self.client.get(url, follow=True)
    #     self.assertEquals(response.status_code, 404)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/create-debate/')
        self.assertEquals(view.func, views.create_debate_view)


class DebateTest(TestCase):
    def setUp(self):
        mock_topic = Topic.objects.create(title='Mock Topic', description='Mock description.')
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='fakepsswrd111')
        Debate.objects.create(topic=mock_topic, starter=mock_user)

    def test_get(self):
        url = reverse('debates:debate', kwargs={'topic_id': 1, 'debate_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/debate:1/')
        self.assertEquals(view.func, views.debate_view)


class DebatesInviteTest(TestCase):
    def setUp(self):
        mock_topic = Topic.objects.create(title='Mock Topic', description='Mock description.')
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='fakepsswrd111')
        Debate.objects.create(topic=mock_topic, starter=mock_user)

    def test_get(self):
        url = reverse('debates:invite', kwargs={'topic_id': 1, 'debate_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/debate:1/invite/')
        self.assertEquals(view.func, views.debates_invite_view)


class UnfollowDebateTest(TestCase):
    def setUp(self):
        mock_topic = Topic.objects.create(title='Mock Topic', description='Mock description.')
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='fakepsswrd111')
        Debate.objects.create(topic=mock_topic, starter=mock_user)

    def test_get(self):
        url = reverse('debates:unfollow', kwargs={'topic_id': 1, 'debate_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/debate:1/unfollow/')
        self.assertEquals(view.func, views.unfollow_debate_view)


class FollowDebateTest(TestCase):
    def setUp(self):
        mock_topic = Topic.objects.create(title='Mock Topic', description='Mock description.')
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='fakepsswrd111')
        Debate.objects.create(topic=mock_topic, starter=mock_user)

    def test_get(self):
        url = reverse('debates:follow', kwargs={'topic_id': 1, 'debate_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/debates/topic:1/debate:1/follow/')
        self.assertEquals(view.func, views.follow_debate_view)
