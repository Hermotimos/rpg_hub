from django.test import TestCase
from django.urls import reverse, resolve
from contact.views import report_view


class ReportTest(TestCase):
    def test_report_view_status_code(self):
        url = reverse('contact:report')
        response = self.client.get(url, follow=True)            # follow=True follows beyond @login_required
        self.assertEquals(response.status_code, 200)

    def test_report_url_resolves_report_view(self):
        view = resolve('/contact/')
        self.assertEquals(view.func, report_view)


