from django.test import TestCase
from django.urls import reverse, resolve
from news import views
from news.models import Survey, SurveyOption, SurveyAnswer
from news.forms import CreateSurveyAnswerForm, CreateSurveyOptionForm
from users.models import User


class DetailTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user1.profile.image = 'profile_pics/profile_Davos.jpg'
        self.user1.profile.save()
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user4 = User.objects.create_user(username='user4', password='pass1111')

        self.survey1 = Survey.objects.create(title='Survey', text='survey1', author=self.user1)
        self.option1 = SurveyOption.objects.create(survey=self.survey1, author=self.user1, option_text='text1')
        self.option2 = SurveyOption.objects.create(survey=self.survey1, author=self.user1, option_text='text2')
        self.survey1.addressees.set([self.user1.profile, self.user2.profile, self.user3.profile])
        self.option1.yes_voters.set([self.user2.profile])
        self.option1.no_voters.set([self.user3.profile])

        self.url = reverse('news:survey-detail', kwargs={'survey_id': self.survey1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user4)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('news:detail', kwargs={'news_id': self.survey1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/news/survey-detail:{self.survey1.id}/')
        self.assertEquals(view.func, views.survey_detail_view)

    def test_links(self):
        linked_url1 = reverse('news:survey-yes', kwargs={'survey_id': self.survey1.id, 'option_id': self.option1.id})
        linked_url2 = reverse('news:survey-no', kwargs={'survey_id': self.survey1.id, 'option_id': self.option1.id})
        linked_url3 = reverse('news:survey-unvote', kwargs={'survey_id': self.survey1.id, 'option_id': self.option1.id})
        linked_url4 = reverse('news:survey-option-modify', kwargs={'survey_id': self.survey1.id,
                                                                   'option_id': self.option2.id})
        linked_url5 = reverse('news:survey-option-delete', kwargs={'survey_id': self.survey1.id,
                                                                   'option_id': self.option2.id})

        # request.user.profile neither in survey1.yes_voters.all() nor in survey1.no_voters.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')
        self.assertContains(response, f'href="{linked_url4}"')
        self.assertContains(response, f'href="{linked_url5}"')

        # request.user.profile in survey1.yes_voters.all()
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')

        # request.user.profile in survey1.no_voters.all()
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    #########################
    # CreateSurveyOptionForm:

    def test_contains_form_1(self):
        # request.user is author
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('option_form')
        self.assertIsInstance(form, CreateSurveyOptionForm)

        # request.user is addressee
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        form = response.context.get('option_form')
        self.assertIsInstance(form, CreateSurveyOptionForm)

    def test_valid_post_data_1(self):
        self.client.force_login(self.user1)
        data = {
            'option_text': 'option3',
        }
        self.assertTrue(SurveyOption.objects.count() == 2)
        self.client.post(self.url, data)
        self.assertTrue(SurveyOption.objects.count() == 3)

    def test_invalid_post_data_1(self):
        self.client.force_login(self.user1)
        data = {}
        self.assertTrue(SurveyOption.objects.count() == 2)
        response = self.client.post(self.url, data)
        form = response.context.get('option_form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(SurveyOption.objects.count() == 2)

    def test_invalid_post_data_empty_fields_1(self):
        self.client.force_login(self.user1)
        data = {
            'option_text': '',
        }
        self.assertTrue(SurveyOption.objects.count() == 2)
        response = self.client.post(self.url, data)
        form = response.context.get('option_form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(SurveyOption.objects.count() == 2)

    #########################
    # CreateSurveyAnswerForm:

    def test_contains_form_2(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('answer_form')
        self.assertIsInstance(form, CreateSurveyAnswerForm)

    def test_valid_post_data_2(self):
        self.client.force_login(self.user1)
        data = {
            'text': 'answer1',
        }
        self.assertFalse(SurveyAnswer.objects.exists())
        self.client.post(self.url, data)
        self.assertTrue(SurveyAnswer.objects.exists())

    def test_invalid_post_data_2(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('answer_form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertFalse(SurveyAnswer.objects.exists())

    def test_invalid_post_data_empty_fields_2(self):
        self.client.force_login(self.user1)
        data = {
            'text': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('answer_form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertFalse(SurveyAnswer.objects.exists())


#######################################################################################################################
# HINT FOR DEBUGGING FORMS' TESTS:
# If test fails, see list of errors for details. Compare it with data sent.
#     data = {
#         'some_data': 'some_value'
#     }
#     print('DATA:\n', data)
#     response = self.client.post(self.url, data)
#     form1 = response.context.get('form1_name')    # by one form usually form_name is just 'form' - depends how in view
#     form2 = response.context.get('form2_name')
#     print('ERRORS:\n', form1.errors)        # To be run multiple times as only first error in form gets printed
#     print('ERRORS:\n', form2.errors)        # To be run multiple times as only first error in form gets printed
