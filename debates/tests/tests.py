from django.test import TestCase
from django.urls import reverse, resolve
from debates import views
from debates.models import Topic, Debate, Remark
from debates.forms import CreateTopicForm, CreateDebateForm, CreateRemarkForm, InviteForm
from users.models import User


class DebatesMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'

        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, name='Debate1', topic=self.topic1, starter=self.user1)
        self.debate2 = Debate.objects.create(id=2, name='Debate2', topic=self.topic1, starter=self.user1)
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

        # case request.user.profile in debate2.allowed_profiles and not in debate1.allowed_profiles
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


class CreateDebateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'

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


class DebateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'gm'

        self.topic1 = Topic.objects.create(id=1, title='Topic1')
        self.debate1 = Debate.objects.create(id=1, topic=self.topic1, starter=self.user1)
        self.debate1.allowed_profiles.set([self.user1.profile, self.user2.profile, ])
        self.debate1.followers.set([self.user1.profile, ])
        self.url = reverse('debates:debate', kwargs={'topic_id': self.topic1.id, 'debate_id': self.debate1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

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
        self.client.post(self.url, data)
        self.assertTrue(Debate.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Remark.objects.exists())
        self.assertTrue(form.errors)

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
        self.assertFalse(Remark.objects.exists())
        self.assertTrue(form.errors)


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
