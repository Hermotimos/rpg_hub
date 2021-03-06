from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand
from users.models import User


class MarkDoneTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.demand1 = Demand.objects.create(author=self.user1, addressee=self.user2, text='Demand1')
        self.url = reverse('contact:done', kwargs={'demand_id': self.demand1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # user3 is neither author nor addressee so is not allowed to mark as done
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('contact:done', kwargs={'demand_id': self.demand1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed_1(self):
        # author is redirected after having marked as done
        self.client.force_login(self.user1)
        redirect_url = reverse('contact:demands-main')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_allowed_2(self):
        # addressee is redirected after having marked as done
        self.client.force_login(self.user2)
        redirect_url = reverse('contact:demands-main')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        # no template generated by mark_done_view()
        pass

    def test_url_resolves_view(self):
        view = resolve(f'/contact/demands/mark-done:{self.demand1.id}/')
        self.assertEquals(view.func, views.mark_done_view)
