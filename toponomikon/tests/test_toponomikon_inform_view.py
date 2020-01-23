from django.test import TestCase
from django.urls import reverse, resolve

from imaginarion.models import Picture
from toponomikon import views
from toponomikon.forms import GeneralLocationInformForm, SpecificLocationInformForm
from toponomikon.models import GeneralLocation, SpecificLocation
from users.models import User


class ToponomikonMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user1.profile.character_status = 'active_player'
        self.user1.profile.save()

        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'inactive_player'
        self.user2.profile.save()

        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.user3.profile.character_status = 'inactive_player'
        self.user3.profile.save()

        self.user4 = User.objects.create_user(username='user4', password='pass1111')
        self.user4.profile.character_status = 'living_npc'
        self.user4.profile.save()

        self.user5 = User.objects.create_user(username='user5', password='pass1111')
        self.user5.profile.character_status = 'gm'
        self.user5.profile.save()

        pic1 = Picture.objects.create(image='post_pics/topoi_anomeia_MAIN.jpg', type='topoi', title='Title1')

        self.gen_loc_1 = GeneralLocation.objects.create(name='GenLoc1', main_image=pic1)
        self.gen_loc_1.known_directly.set([self.user1.profile])
        self.gen_loc_1.known_indirectly.set([self.user2.profile])

        self.spec_loc_1 = SpecificLocation.objects.create(name='SpecLoc1', general_location=self.gen_loc_1,
                                                          main_image=pic1)
        self.spec_loc_1.known_directly.set([self.user1.profile])
        self.spec_loc_1.known_indirectly.set([self.user2.profile])

        self.url_1 = reverse('toponomikon:inform', kwargs={'gen_loc_id': self.gen_loc_1.id, 'spec_loc_id': 0})
        self.url_2 = reverse('toponomikon:inform', kwargs={'gen_loc_id': 0, 'spec_loc_id': self.spec_loc_1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url_1
        response = self.client.get(self.url_1)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')

        response = self.client.get(self.url_1)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        response = self.client.get(self.url_2)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)

        url = reverse('toponomikon:inform', kwargs={'gen_loc_id': self.gen_loc_1.id + 999, 'spec_loc_id': 0})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

        url = reverse('toponomikon:inform', kwargs={'gen_loc_id': 0, 'spec_loc_id': self.spec_loc_1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url_1)
        self.assertEquals(response.status_code, 200)

        self.client.force_login(self.user1)
        response = self.client.get(self.url_2)
        self.assertEquals(response.status_code, 200)

        self.client.force_login(self.user2)
        response = self.client.get(self.url_1)
        self.assertEquals(response.status_code, 200)

        self.client.force_login(self.user2)
        response = self.client.get(self.url_2)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/toponomikon/gen-loc:{self.gen_loc_1.id}/spec-loc:0/inform/')
        self.assertEquals(view.func, views.toponomikon_inform_view)

        view = resolve(f'/toponomikon/gen-loc:0/spec-loc:{self.spec_loc_1.id}/inform/')
        self.assertEquals(view.func, views.toponomikon_inform_view)

    #################################################
    # FOR url_1 i.e. form = GeneralLocationInformForm
    #################################################

    def test_valid_post_data_1a(self):
        # request.user.profile in known_directly informs uninformed user
        self.client.force_login(self.user1)
        form = GeneralLocationInformForm(authenticated_user=self.user1,
                                         known_directly_old=self.gen_loc_1.known_directly.all(),
                                         known_indirectly_old=self.gen_loc_1.known_indirectly.all(),
                                         instance=self.gen_loc_1)
        data = form.initial
        data['known_indirectly'] = [self.user3.profile.id]
        self.assertFalse(self.user3.profile in GeneralLocation.objects.get(id=1).known_indirectly.all())
        self.client.post(self.url_1, data)
        self.assertTrue(self.user3.profile in GeneralLocation.objects.get(id=1).known_indirectly.all())

    def test_valid_post_data_1b(self):
        # request.user.profile in known_indirectly informs uninformed user
        self.client.force_login(self.user2)
        form = GeneralLocationInformForm(authenticated_user=self.user2,
                                         known_directly_old=self.gen_loc_1.known_directly.all(),
                                         known_indirectly_old=self.gen_loc_1.known_indirectly.all(),
                                         instance=self.gen_loc_1)
        data = form.initial
        data['known_indirectly'] = [self.user3.profile.id]
        self.assertFalse(self.user3.profile in GeneralLocation.objects.get(id=1).known_indirectly.all())
        self.client.post(self.url_1, data)
        self.assertTrue(self.user3.profile in GeneralLocation.objects.get(id=1).known_indirectly.all())

    def test_invalid_post_data_1(self):
        self.client.force_login(self.user1)
        form = GeneralLocationInformForm(authenticated_user=self.user2,
                                         known_directly_old=self.gen_loc_1.known_directly.all(),
                                         known_indirectly_old=self.gen_loc_1.known_indirectly.all(),
                                         instance=self.gen_loc_1)
        data = form.initial
        data['known_indirectly'] = 'Invalid data'
        response = self.client.post(self.url_1, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields_1(self):
        self.client.force_login(self.user1)
        form = GeneralLocationInformForm(authenticated_user=self.user2,
                                         known_directly_old=self.gen_loc_1.known_directly.all(),
                                         known_indirectly_old=self.gen_loc_1.known_indirectly.all(),
                                         instance=self.gen_loc_1)
        data = form.initial
        data['known_indirectly'] = ''
        response = self.client.post(self.url_1, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    #################################################
    # FOR url_2 i.e. form = SpecificLocationInformForm
    #################################################

    def test_valid_post_data_2a(self):
        # request.user.profile in known_directly informs uninformed user
        self.client.force_login(self.user1)
        form = SpecificLocationInformForm(authenticated_user=self.user1,
                                          known_directly_old=self.spec_loc_1.known_directly.all(),
                                          known_indirectly_old=self.spec_loc_1.known_indirectly.all(),
                                          instance=self.spec_loc_1)
        data = form.initial
        data['known_indirectly'] = [self.user3.profile.id]
        self.assertFalse(self.user3.profile in SpecificLocation.objects.get(id=1).known_indirectly.all())
        self.client.post(self.url_2, data)
        self.assertTrue(self.user3.profile in SpecificLocation.objects.get(id=1).known_indirectly.all())

    def test_valid_post_data_2b(self):
        # request.user.profile in known_indirectly informs uninformed user
        self.client.force_login(self.user2)
        form = SpecificLocationInformForm(authenticated_user=self.user2,
                                          known_directly_old=self.spec_loc_1.known_directly.all(),
                                          known_indirectly_old=self.spec_loc_1.known_indirectly.all(),
                                          instance=self.spec_loc_1)
        data = form.initial
        data['known_indirectly'] = [self.user3.profile.id]
        self.assertFalse(self.user3.profile in SpecificLocation.objects.get(id=1).known_indirectly.all())
        self.client.post(self.url_2, data)
        self.assertTrue(self.user3.profile in SpecificLocation.objects.get(id=1).known_indirectly.all())

    def test_invalid_post_data_2(self):
        self.client.force_login(self.user1)
        form = SpecificLocationInformForm(authenticated_user=self.user2,
                                          known_directly_old=self.spec_loc_1.known_directly.all(),
                                          known_indirectly_old=self.spec_loc_1.known_indirectly.all(),
                                          instance=self.spec_loc_1)
        data = form.initial
        data['known_indirectly'] = 'Invalid data'
        response = self.client.post(self.url_2, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields_2(self):
        self.client.force_login(self.user1)
        form = SpecificLocationInformForm(authenticated_user=self.user2,
                                          known_directly_old=self.spec_loc_1.known_directly.all(),
                                          known_indirectly_old=self.spec_loc_1.known_indirectly.all(),
                                          instance=self.spec_loc_1)
        data = form.initial
        data['known_indirectly'] = ''
        response = self.client.post(self.url_2, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)


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
