from django.test import TestCase
from django.urls import reverse, resolve
from news import views
from news.models import Survey, SurveyOption
from users.models import User


class VoteNoTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')

        self.survey1 = Survey.objects.create(title='Survey1', text='survey1', author=self.user1)
        self.survey1.addressees.set([self.user1.profile])
        self.option1 = SurveyOption.objects.create(survey=self.survey1, author=self.user1, option_text='text1')

        self.url = reverse('news:survey-no', kwargs={'survey_id': self.survey1.id, 'option_id': self.option1.id})

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
        url = reverse('news:survey-no', kwargs={'survey_id': self.survey1.id, 'option_id': self.option1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed(self):
        self.client.force_login(self.user1)
        redirect_url = reverse('news:survey-detail', kwargs={'survey_id': self.survey1.id})
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        # no template generated by vote_no_view()
        pass

    def test_url_resolves_view(self):
        view = resolve(f'/news/survey-detail:{self.survey1.id}/survey-option:{self.survey1.id}/no')
        self.assertEquals(view.func, views.vote_no_view)
