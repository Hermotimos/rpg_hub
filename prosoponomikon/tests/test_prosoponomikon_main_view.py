from django.test import TestCase
from django.urls import reverse, resolve

from prosoponomikon import views
from users.models import User


class ToponomikonMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user1.profile.character_status = 'active_player'
        self.user1.profile.save()

        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'gm'
        self.user2.profile.save()

        self.url = reverse('prosoponomikon:main')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/prosoponomikon/')
        self.assertEquals(view.func, views.prosoponomikon_main_view)

    # def test_links(self):
    #     linked_url1 = reverse('prosoponomikon:XXXXXXXXXXXXX', kwargs={'profile_id': self.user1.profile.id})
