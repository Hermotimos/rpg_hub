from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand
from users.models import User


class MainTest(TestCase):
    def setUp(self):
        url = reverse('contact:main')
        self.response = self.client.get(url, follow=True)

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/')
        self.assertEquals(view.func, views.demands_view)


class CreateDemandTest(TestCase):
    def setUp(self):
        url = reverse('contact:main')
        self.response = self.client.get(url, follow=True)

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/create')
        self.assertEquals(view.func, views.create_demand_view)

    def test_contains_link_to_main(self):
        linked_url = reverse('debates:main')
        self.assertContains(self.response, f'href="{linked_url}"')


class DeleteDemandTest(TestCase):
    def setUp(self):
        url = reverse('contact:main')
        self.response = self.client.get(url, follow=True)

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/delete:1/')
        self.assertEquals(view.func, views.delete_demand_view)

    def test_contains_link_to_main(self):
        linked_url = reverse('debates:main')
        self.assertContains(self.response, f'href="{linked_url}"')


class ModifyDemandTest(TestCase):
    def setUp(self):
        url = reverse('contact:main')
        self.response = self.client.get(url, follow=True)

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/modify:1/')
        self.assertEquals(view.func, views.modify_demand_view)

    def test_contains_link_to_main(self):
        linked_url = reverse('debates:main')
        self.assertContains(self.response, f'href="{linked_url}"')


class DemandDetailTest(TestCase):
    def setUp(self):
        url = reverse('contact:main')
        self.response = self.client.get(url, follow=True)

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/detail:1/')
        self.assertEquals(view.func, views.demand_detail_view)

    def test_contains_link_to_main(self):
        linked_url = reverse('debates:main')
        self.assertContains(self.response, f'href="{linked_url}"')


class MarkDoneTest(TestCase):
    def setUp(self):
        url = reverse('contact:main')
        self.response = self.client.get(url, follow=True)

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/mark-done:1/')
        self.assertEquals(view.func, views.mark_done_view)

    def test_contains_link_to_main(self):
        linked_url = reverse('debates:main')
        self.assertContains(self.response, f'href="{linked_url}"')


class MarkUndoneTest(TestCase):
    def setUp(self):
        url = reverse('contact:main')
        self.response = self.client.get(url, follow=True)

        mock_user = User.objects.create_user(username='mock_user', email='mock@user.com', password='mockpsswrd111')
        mock_user2 = User.objects.create_user(username='mock_user2', email='mock2@user.com', password='mockpsswrd111')
        Demand.objects.create(author=mock_user, addressee=mock_user2, text='Mock report')

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/mark-undone:1/')
        self.assertEquals(view.func, views.mark_undone_view)

    def test_contains_link_to_main(self):
        linked_url = reverse('debates:main')
        self.assertContains(self.response, f'href="{linked_url}"')
