from django.test import TestCase
from django.urls import reverse, resolve
from rules.views import rules_main_view


class RulesMainTest(TestCase):
    def test_get(self):
        url = reverse('rules:main')
        response = self.client.get(url, follow=True)            # follow=True follows beyond @login_required
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/rules/')
        self.assertEquals(view.func, rules_main_view)