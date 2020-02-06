from django.test import TestCase
from django.urls import reverse, resolve

from knowledge import views
from knowledge.forms import KnowledgePacketInformForm
from knowledge.models import KnowledgePacket
from users.models import User


class KnowledgeInformTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'active_player'
        self.user2.profile.save()

        self.user3 = User.objects.create_user(username='user4', password='pass1111')
        self.user3.profile.character_status = 'gm'
        self.user3.profile.save()

        self.kn_packet_1 = KnowledgePacket.objects.create(title='KnPacket1', text='Text1')
        self.kn_packet_1.allowed_profiles.set([self.user1.profile])

        self.url = reverse('knowledge:inform', kwargs={'kn_packet_id': self.kn_packet_1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # request.user.profile neither in kn_packet_1.allowed_profiles.all() nor character_status == 'gm'
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('knowledge:inform', kwargs={'kn_packet_id': self.kn_packet_1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        # request.user.profile in kn_packet_1.allowed_profiles.all()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

        # request.user.profile.character_status == 'gm'
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/knowledge/inform:{self.kn_packet_1.id}/')
        self.assertEquals(view.func, views.knowledge_inform_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, KnowledgePacketInformForm)

    def test_valid_post_data1(self):
        # allowed user1 informs an unallowed user2
        self.client.force_login(self.user1)
        form = KnowledgePacketInformForm(authenticated_user=self.user1,
                                         already_allowed_profiles=[self.user1.profile.id, ],
                                         instance=self.kn_packet_1)
        data = form.initial
        data['allowed_profiles'] = [self.user2.profile.id]
        self.assertFalse(self.user2.profile in KnowledgePacket.objects.get(id=1).allowed_profiles.all())
        self.client.post(self.url, data)
        self.assertTrue(self.user2.profile in KnowledgePacket.objects.get(id=1).allowed_profiles.all())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        form = KnowledgePacketInformForm(authenticated_user=self.user1,
                                         already_allowed_profiles=[self.user1.profile.id, ],
                                         instance=self.kn_packet_1)
        data = form.initial
        data['allowed_profiles'] = 'Invalid data'
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        form = KnowledgePacketInformForm(authenticated_user=self.user1,
                                         already_allowed_profiles=[self.user1.profile.id, ],
                                         instance=self.kn_packet_1)
        data = form.initial
        data['allowed_profiles'] = ''
        response = self.client.post(self.url, data)
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
