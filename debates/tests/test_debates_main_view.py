from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate
from users.models import User


class DebatesMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'
        self.user4.profile.save()

        self.topic1 = Topic.objects.create(title='Topic1')
        self.debate1 = Debate.objects.create(name='Debate1', topic=self.topic1, starter=self.user1)
        self.debate2 = Debate.objects.create(name='Debate2', topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, ])
        self.debate2.allowed_profiles.set([self.user3.profile, ])

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

        # request.user.profile in debate1.allowed_profiles
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')

        # request.user.profile not in debate1.allowed_profiles
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')

        # request.user.profile in debate2.allowed_profiles and not in debate1.allowed_profiles
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')

        # case request.user.profile.character_status == 'gm'
        self.client.force_login(self.user4)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
