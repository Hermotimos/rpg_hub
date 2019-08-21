from django.test import TestCase
from django.urls import reverse, resolve
from contact  import views
from contact.models import Demand
from users.models import User


class ReportTest(TestCase):
    def test_get(self):
        url = reverse('contact:report')
        response = self.client.get(url, follow=True)            # follow=True follows beyond @login_required
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/')
        self.assertEquals(view.func, views.create_demand_view)


class ReportsListTest(TestCase):
    def setUp(self):
        mock_user = User.objects.create_user(username='test_user', email='test@user.com', password='sswapord123')
        Demand.objects.create(author=mock_user, text='Mock report')

    def test_get(self):
        url = reverse('contact:reports-list')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/reports-list/')
        self.assertEquals(view.func, views.main_view)