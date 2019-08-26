from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand
from users.models import User


# ------------------- DEMANDS -------------------


class DemandsMainTest(TestCase):
    def test_get(self):
        url = reverse('contact:demands-main')
        self.response = self.client.get(url, follow=True)
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/main/')
        self.assertEquals(view.func, views.demands_main_view)


class DemandsCreateTest(TestCase):
    def test_get(self):
        url = reverse('contact:demands-create')
        self.response = self.client.get(url, follow=True)
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/create/')
        self.assertEquals(view.func, views.demands_create_view)


class DemandsDeleteTest(TestCase):
    def setUp(self):

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):

        url = reverse('contact:demands-delete', kwargs={'demand_id': 1})
        self.response = self.client.get(url, follow=True)
        self.assertEquals(self.response.status_code, 200)

    def test_redirect_if_unallowed(self):
        pass

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/delete:1/')
        self.assertEquals(view.func, views.demands_delete_view)


class DemandsModifyTest(TestCase):
    def setUp(self):

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):
        url = reverse('contact:demands-modify', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/modify:1/')
        self.assertEquals(view.func, views.demands_modify_view)


class DemandsDetailTest(TestCase):
    def setUp(self):

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):
        url = reverse('contact:demands-detail', kwargs={'demand_id': 1})
        self.response = self.client.get(url, follow=True)
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/detail:1/')
        self.assertEquals(view.func, views.demands_detail_view)


# ------------------- PLANS -------------------


class PlansMainTest(TestCase):
    def test_get(self):
        url = reverse('contact:plans-main')
        self.response = self.client.get(url, follow=True)
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/plans/main/')
        self.assertEquals(view.func, views.plans_main_view)


class PlansCreateTest(TestCase):
    def test_get(self):
        url = reverse('contact:plans-create')
        self.response = self.client.get(url, follow=True)
        self.assertEquals(self.response.status_code, 200)

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
        self.response = self.client.get(url, follow=True)
        self.assertEquals(self.response.status_code, 200)

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
        self.response = self.client.get(url, follow=True)
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/mark-undone:1/')
        self.assertEquals(view.func, views.mark_undone_view)
