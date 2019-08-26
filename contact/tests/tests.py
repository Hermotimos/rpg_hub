from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand
from users.models import User


# ------------------- DEMANDS -------------------


class DemandsMainTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='fakepsswrd111')
        self.client.force_login(mock_user)

    def test_login_required(self):
        self.client.logout()
        url = reverse('contact:demands-main')
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        url = reverse('contact:demands-main')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/main/')
        self.assertEquals(view.func, views.demands_main_view)


class DemandsCreateTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='fakepsswrd111')
        self.client.force_login(mock_user)

    def test_login_required(self):
        self.client.logout()
        url = reverse('contact:demands-create')
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        url = reverse('contact:demands-create')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/create/')
        self.assertEquals(view.func, views.demands_create_view)


class DemandsDeleteTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='fakepsswrd111')
        self.client.force_login(mock_user)
        Demand.objects.create(id=1, author=mock_user, addressee=mock_user, text='Mock demand')

    def test_login_required(self):
        self.client.logout()
        url = reverse('contact:demands-delete', kwargs={'demand_id': 1})
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock@user2.com', password='fakepsswrd111')
        self.client.force_login(mock_user2)
        url = reverse('contact:demands-delete', kwargs={'demand_id': 1})
        redirect_url = reverse('home:dupa')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        url = reverse('contact:demands-delete', kwargs={'demand_id': 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed(self):
        url = reverse('contact:demands-delete', kwargs={'demand_id': 1})
        redirect_url = reverse('contact:demands-main')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/delete:1/')
        self.assertEquals(view.func, views.demands_delete_view)

    # No test_get - no template generated


class DemandsModifyTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='fakepsswrd111')
        self.client.force_login(mock_user)
        Demand.objects.create(id=1, author=mock_user, addressee=mock_user, text='Mock demand')

    def test_login_required(self):
        self.client.logout()
        url = reverse('contact:demands-modify', kwargs={'demand_id': 1})
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock@user2.com', password='fakepsswrd111')
        self.client.force_login(mock_user2)
        url = reverse('contact:demands-modify', kwargs={'demand_id': 1})
        redirect_url = reverse('home:dupa')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        url = reverse('contact:demands-modify', kwargs={'demand_id': 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        url = reverse('contact:demands-modify', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/modify:1/')
        self.assertEquals(view.func, views.demands_modify_view)


class DemandsDetailTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='fakepsswrd111')
        self.client.force_login(mock_user)
        Demand.objects.create(id=1, author=mock_user, addressee=mock_user, text='Mock demand')

    def test_login_required(self):
        self.client.logout()
        url = reverse('contact:demands-detail', kwargs={'demand_id': 1})
        redirect_url = reverse('users:login') + '?next=' + url
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock@user2.com', password='fakepsswrd111')
        self.client.force_login(mock_user2)
        url = reverse('contact:demands-detail', kwargs={'demand_id': 1})
        redirect_url = reverse('home:dupa')
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        url = reverse('contact:demands-detail', kwargs={'demand_id': 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        url = reverse('contact:demands-detail', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/detail:1/')
        self.assertEquals(view.func, views.demands_detail_view)


# ------------------- PLANS -------------------


class PlansMainTest(TestCase):
    def test_get(self):
        url = reverse('contact:plans-main')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/plans/main/')
        self.assertEquals(view.func, views.plans_main_view)


class PlansCreateTest(TestCase):
    def test_get(self):
        url = reverse('contact:plans-create')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/plans/create/')
        self.assertEquals(view.func, views.plans_create_view)


# ------------------- DEMANDS & PLANS -------------------


class MarkDoneTest(TestCase):
    def setUp(self):

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):
        url = reverse('contact:done', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/mark-done:1/')
        self.assertEquals(view.func, views.mark_done_view)


class MarkUndoneTest(TestCase):
    def setUp(self):

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):
        url = reverse('contact:undone', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/mark-undone:1/')
        self.assertEquals(view.func, views.mark_undone_view)
