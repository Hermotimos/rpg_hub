from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand
from users.models import User


class MainTest(TestCase):
    def test_get(self):
        url = reverse('contact:main')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/')
        self.assertEquals(view.func, views.main_view)


class CreateDemandTest(TestCase):
    def test_get(self):
        url = reverse('contact:create')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/create')
        self.assertEquals(view.func, views.create_demand_view)


class DeleteDemandTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, text='Mock report')

    def test_get(self):
        url = reverse('contact:delete', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/delete:1/')
        self.assertEquals(view.func, views.delete_demand_view)


class ModifyDemandTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, text='Mock report')

    def test_get(self):
        url = reverse('contact:modify', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/modify:1/')
        self.assertEquals(view.func, views.modify_demand_view)


class DemandDetailTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, text='Mock report')

    def test_get(self):
        url = reverse('contact:detail', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/detail:1/')
        self.assertEquals(view.func, views.demand_detail_view)


class MarkDoneTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, text='Mock report')

    def test_get(self):
        url = reverse('contact:done', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/mark-done:1/')
        self.assertEquals(view.func, views.mark_done_view)


class MarkDoneAndAnswerDemandTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, text='Mock report')

    def test_get(self):
        url = reverse('contact:done-answer', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/mark-done:1/answer/')
        self.assertEquals(view.func, views.mark_done_and_answer_view)


class MarkUndoneTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, text='Mock report')

    def test_get(self):
        url = reverse('contact:undone', kwargs={'demand_id': 1})
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/mark-undone:1/')
        self.assertEquals(view.func, views.mark_undone_view)
