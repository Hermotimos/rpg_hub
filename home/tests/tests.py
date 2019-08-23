from django.test import TestCase
from django.urls import reverse, resolve
from home import views


class LinksToAppsTest(TestCase):
    def setUp(self):
        url = reverse('home:home')
        self.response = self.client.get(url, follow=True)

    def test_get(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/home')
        self.assertEquals(view.func, views.home_view)

    def test_contains_link_to_apps(self):
        url_news = reverse('news:main')
        url_rules = reverse('rules:main')
        url_demands = reverse('contact:demands-main')
        url_chronicle = reverse('history:chronicle-main')
        url_timeline = reverse('history:timeline-main')
        url_debates = reverse('debates:main')
        url_users_profile = reverse('users:profile')
        url_users_logout = reverse('users:logout')
        url_demands_create = reverse('contact:demands-create')
        url_plans = reverse('contact:plans-main')
        # url_admin = reverse('admin:index')

        self.assertContains(self.response, f'href="{url_news}"')
        self.assertContains(self.response, f'href="{url_rules}"')
        self.assertContains(self.response, f'href="{url_demands}"')
        self.assertContains(self.response, f'href="{url_chronicle}"')
        self.assertContains(self.response, f'href="{url_timeline}"')
        self.assertContains(self.response, f'href="{url_debates}"')
        self.assertContains(self.response, f'href="{url_users_profile}"')
        self.assertContains(self.response, f'href="{url_users_logout}"')
        self.assertContains(self.response, f'href="{url_demands_create}"')
        self.assertContains(self.response, f'href="{url_plans}"')
        # self.assertContains(self.response, f'href="{url_admin}"')
