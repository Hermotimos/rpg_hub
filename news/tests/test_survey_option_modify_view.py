from django.test import TestCase
from django.urls import reverse, resolve
from news import views
from news.models import Survey, SurveyOption
from news.forms import ModifySurveyOptionForm
from users.models import User


class SurveyOptionModifyTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')

        self.survey1 = Survey.objects.create(title='Survey1', text='survey1', author=self.user1)
        self.survey1.addressees.set([self.user1.profile])
        self.option1 = SurveyOption.objects.create(survey=self.survey1, author=self.user1, option_text='text1')

        self.url = reverse('news:survey-option-modify', kwargs={'survey_id': self.survey1.id,
                                                                'option_id': self.option1.id})

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
        url = reverse('news:survey-detail', kwargs={'survey_id': self.survey1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/news/survey-detail:{self.survey1.id}/survey-option:{self.survey1.id}/modify')
        self.assertEquals(view.func, views.survey_option_modify_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        # request.user is author
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, ModifySurveyOptionForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'option_text': 'changed',
        }
        self.assertTrue(SurveyOption.objects.get(id=1).option_text == 'text1')
        self.client.post(self.url, data)
        self.assertTrue(SurveyOption.objects.get(id=1).option_text == 'changed')

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'option_text': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
