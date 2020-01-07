from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate, Remark
from debates.forms import CreateRemarkForm
from users.models import User


class DebateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'

        self.topic1 = Topic.objects.create(title='Topic1')
        self.debate1 = Debate.objects.create(topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, self.user2.profile, ])
        self.debate1.followers.set([self.user1.profile, ])

        self.url = reverse('debates:debate', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # user3 not in debate.allowed_profiles.all()
        self.client.force_login(self.user3)
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

        # user1 in debate.followers
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')

        # user2 not in debate.followers
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, CreateRemarkForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'text': 'Text1',
            'debate': self.debate1.id,
            'author': self.user1.id
        }
        self.assertFalse(Remark.objects.exists())
        self.client.post(self.url, data)
        self.assertTrue(Remark.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertFalse(Remark.objects.exists())

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'text': '',
            'debate': '',
            'author': ''
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertFalse(Remark.objects.exists())
