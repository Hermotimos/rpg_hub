from django.test import TestCase
from django.urls import reverse, resolve
from contact import views
from contact.models import Demand, Plan, DemandAnswer
from contact.forms import DemandsCreateForm, DemandsModifyForm, DemandAnswerForm, PlansCreateForm, PlansModifyForm
from users.models import User


# ------------------- DEMANDS -------------------


class DemandsMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.demand1 = Demand.objects.create(id=1, author=self.user1, addressee=self.user2, text='Demand1')
        self.demand2 = Demand.objects.create(id=2, author=self.user1, addressee=self.user2, text='Demand2',
                                             is_done=True)
        self.url = reverse('contact:demands-main')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/main/')
        self.assertEquals(view.func, views.demands_main_view)

    def test_links(self):
        linked_url1 = reverse('contact:demands-create')
        # demand1.is_done=False
        linked_url2 = reverse('contact:demands-modify', kwargs={'demand_id': self.demand1.id})
        linked_url3 = reverse('contact:done', kwargs={'demand_id': self.demand1.id})
        linked_url4 = reverse('contact:undone', kwargs={'demand_id': self.demand1.id})
        linked_url5 = reverse('contact:demands-delete', kwargs={'demand_id': self.demand1.id})
        # demand2.is_done=True
        linked_url6 = reverse('contact:demands-modify', kwargs={'demand_id': self.demand2.id})
        linked_url7 = reverse('contact:done', kwargs={'demand_id': self.demand2.id})
        linked_url8 = reverse('contact:undone', kwargs={'demand_id': self.demand2.id})
        linked_url9 = reverse('contact:demands-delete', kwargs={'demand_id': self.demand2.id})

        # case request.user is author
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')
        self.assertNotContains(response, f'href="{linked_url6}"')
        self.assertNotContains(response, f'href="{linked_url7}"')
        self.assertContains(response, f'href="{linked_url8}"')
        self.assertContains(response, f'href="{linked_url9}"')

        # # case request.user is addressee
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')
        self.assertNotContains(response, f'href="{linked_url6}"')
        self.assertNotContains(response, f'href="{linked_url7}"')
        self.assertContains(response, f'href="{linked_url8}"')
        self.assertNotContains(response, f'href="{linked_url9}"')

        # # case request.user is neither author nor addressee
        self.client.force_login(self.user3)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')
        self.assertNotContains(response, f'href="{linked_url4}"')
        self.assertNotContains(response, f'href="{linked_url5}"')
        self.assertNotContains(response, f'href="{linked_url6}"')
        self.assertNotContains(response, f'href="{linked_url7}"')
        self.assertNotContains(response, f'href="{linked_url8}"')
        self.assertNotContains(response, f'href="{linked_url9}"')


class DemandsCreateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user2.profile.character_status = 'active_player'
        self.user2.save()
        self.url = reverse('contact:demands-create')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/demands/create/')
        self.assertEquals(view.func, views.demands_create_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, DemandsCreateForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'addressee': self.user2.id,     # by ForeignKeyField pk or id has to be provided
            'text': 'demand2',
        }
        self.client.post(self.url, data)
        self.assertTrue(Demand.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'addressee': '',
            'text': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Demand.objects.exists())
        self.assertTrue(form.errors)


class DemandsDeleteTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.demand1 = Demand.objects.create(id=1, author=self.user1, addressee=self.user2, text='Demand1')
        self.url = reverse('contact:demands-delete', kwargs={'demand_id': self.demand1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # case addressee is not allowed to delete
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('contact:demands-delete', kwargs={'demand_id': self.demand1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed(self):
        self.client.force_login(self.user1)
        redirect_url = reverse('contact:demands-main')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # def test_get(self): - no template generated by demands_delete_view()

    def test_url_resolves_view(self):
        view = resolve(f'/contact/demands/delete:{self.demand1.id}/')
        self.assertEquals(view.func, views.demands_delete_view)


class DemandsModifyTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.demand1 = Demand.objects.create(id=1, author=self.user1, addressee=self.user2, text='Demand1')
        self.url = reverse('contact:demands-modify', kwargs={'demand_id': self.demand1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        # case addressee is not allowed to modify
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('contact:demands-modify', kwargs={'demand_id': self.demand1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/contact/demands/modify:{self.demand1.id}/')
        self.assertEquals(view.func, views.demands_modify_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, DemandsModifyForm)

    # # TODO Nonsense error for field image with null=True, blank=True:
    # # ValueError: The 'image' attribute has no file associated with it.
    # def test_valid_post_data(self):
    #     self.client.force_login(self.user1)
    #     form = DemandsModifyForm(instance=self.demand1)
    #     data = form.initial
    #     data['text'] = 'changed text'
    #     print('\n', data)
    #     response = self.client.post(self.url, data)
    #     form = response.context.get('form')
    #     print('\n', form.errors)
    #
    #     # self.client.post(self.url, data)
    #     self.assertTrue(Demand.objects.get(id=1).text == 'changed text')

    # # TODO Nonsense error for field image with null=True, blank=True:
    # # ValueError: The 'image' attribute has no file associated with it.
    # def test_invalid_post_data(self):
    #     self.client.force_login(self.user1)
    #     form = DemandsModifyForm(instance=self.demand1)
    #     data = form.initial
    #     data['is_done'] = 'Invalid data for BooleanField'
    #     response = self.client.post(self.url, data)
    #     form = response.context.get('form')
    #     # should show the form again, not redirect
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTrue(form.errors)

    # # TODO Nonsense error for field image with null=True, blank=True:
    # # ValueError: The 'image' attribute has no file associated with it.
    # def test_invalid_post_data_empty_fields(self):
    #     self.client.force_login(self.user1)
    #     form = DemandsModifyForm(instance=self.demand1)
    #     data = form.initial
    #     data['text'] = ''
    #     response = self.client.post(self.url, data)
    #     form = response.context.get('form')
    #     # should show the form again, not redirect
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTrue(form.errors)
    #     self.assertTrue(Demand.objects.get(id=1).text == 'Demand1')


class DemandsDetailTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.demand1 = Demand.objects.create(id=1, author=self.user1, addressee=self.user2, text='Demand1')
        self.url = reverse('contact:demands-detail', kwargs={'demand_id': self.demand1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('contact:demands-detail', kwargs={'demand_id': self.demand1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get_1(self):
        # test for author
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_get_2(self):
        # test for addressee
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/contact/demands/detail:{self.demand1.id}/')
        self.assertEquals(view.func, views.demands_detail_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, DemandAnswerForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'text': 'Answer text',
        }
        self.client.post(self.url, data)
        self.assertTrue(DemandAnswer.objects.exists())

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'text': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertFalse(DemandAnswer.objects.exists())
        self.assertTrue(form.errors)


class MarkDoneTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.demand1 = Demand.objects.create(id=1, author=self.user1, addressee=self.user2, text='Demand1')
        self.url = reverse('contact:done', kwargs={'demand_id': self.demand1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
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
        self.client.force_login(self.user1)
        redirect_url = reverse('contact:demands-main')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_allowed_2(self):
        self.client.force_login(self.user2)
        redirect_url = reverse('contact:demands-main')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # No test_get - no template generated by mark_done_view()

    def test_url_resolves_view(self):
        view = resolve(f'/contact/demands/mark-done:{self.demand1.id}/')
        self.assertEquals(view.func, views.mark_done_view)


class MarkUndoneTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user3 = User.objects.create_user(username='user3', password='pass1111')
        self.demand1 = Demand.objects.create(id=1, author=self.user1, addressee=self.user2, text='Demand1')
        self.url = reverse('contact:done', kwargs={'demand_id': self.demand1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user3)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('contact:undone', kwargs={'demand_id': self.demand1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed_1(self):
        self.client.force_login(self.user1)
        redirect_url = reverse('contact:demands-main')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_allowed_2(self):
        self.client.force_login(self.user2)
        redirect_url = reverse('contact:demands-main')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # No test_get - no template generated by mark_undone_view()

    def test_url_resolves_view(self):
        view = resolve(f'/contact/demands/mark-undone:{self.demand1.id}/')
        self.assertEquals(view.func, views.mark_undone_view)


# ------------------- PLANS -------------------


class PlansMainTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.plan1 = Plan.objects.create(id=1, author=self.user1)

        self.url = reverse('contact:plans-main')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/plans/main/')
        self.assertEquals(view.func, views.plans_main_view)

    def test_links(self):
        linked_url1 = reverse('contact:plans-create')
        linked_url2 = reverse('contact:plans-modify', kwargs={'plan_id': self.plan1.id})
        linked_url3 = reverse('contact:plans-delete', kwargs={'plan_id': self.plan1.id})

        # case request.user is author
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertContains(response, f'href="{linked_url2}"')
        self.assertContains(response, f'href="{linked_url3}"')

        # case request.user is not author
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertContains(response, f'href="{linked_url1}"')
        self.assertNotContains(response, f'href="{linked_url2}"')
        self.assertNotContains(response, f'href="{linked_url3}"')


class PlansForGmTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.user1.profile.character_status = 'gm'
        self.url = reverse('contact:plans-for-gm')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        # case user.profile.character_status == 'gm' is allowed to plans_for_gm_view()
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/plans/for-gm/')
        self.assertEquals(view.func, views.plans_for_gm_view)


class PlansCreateTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.url = reverse('contact:plans-create')

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve('/contact/plans/create/')
        self.assertEquals(view.func, views.plans_create_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, PlansCreateForm)

    def test_valid_post_data(self):
        self.client.force_login(self.user1)
        data = {
            'text': 'plan2',
        }
        self.client.post(self.url, data)
        self.assertTrue(Plan.objects.count() == 1)

    def test_invalid_post_data(self):
        self.client.force_login(self.user1)
        data = {}
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(Plan.objects.count() == 0)

    def test_invalid_post_data_empty_fields(self):
        self.client.force_login(self.user1)
        data = {
            'text': '',
        }
        response = self.client.post(self.url, data)
        form = response.context.get('form')
        # should show the form again, not redirect
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)
        self.assertTrue(Plan.objects.count() == 0)


class PlansDeleteTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.plan1 = Plan.objects.create(id=1, author=self.user1)
        self.url = reverse('contact:plans-delete', kwargs={'plan_id': self.plan1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('contact:plans-delete', kwargs={'plan_id': self.plan1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_redirect_if_allowed(self):
        self.client.force_login(self.user1)
        redirect_url = reverse('contact:plans-main')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # No test_get - no template generated by mark_undone_view()

    def test_url_resolves_view(self):
        view = resolve(f'/contact/plans/delete:{self.plan1.id}/')
        self.assertEquals(view.func, views.plans_delete_view)


class PlansModifyTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass1111')
        self.user2 = User.objects.create_user(username='user2', password='pass1111')
        self.plan1 = Plan.objects.create(id=1, author=self.user1, text='Plan1')
        self.url = reverse('contact:plans-modify', kwargs={'plan_id': self.plan1.id})

    def test_login_required(self):
        redirect_url = reverse('users:login') + '?next=' + self.url
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_redirect_if_unallowed(self):
        self.client.force_login(self.user2)
        redirect_url = reverse('home:dupa')
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_404(self):
        self.client.force_login(self.user1)
        url = reverse('contact:plans-modify', kwargs={'plan_id': self.plan1.id + 999})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_get(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_url_resolves_view(self):
        view = resolve(f'/contact/plans/modify:{self.plan1.id}/')
        self.assertEquals(view.func, views.plans_modify_view)

    def test_csrf(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)
        form = response.context.get('form')
        self.assertIsInstance(form, PlansModifyForm)

    # # TODO Nonsense error for field image with null=True, blank=True:
    # # ValueError: The 'image' attribute has no file associated with it.
    # def test_valid_post_data(self):
    #     self.client.force_login(self.user1)
    #     form = PlansModifyForm(instance=self.plan1)
    #     data = form.initial
    #     data['text'] = 'changed text'
    #     print('\n', data)
    #     response = self.client.post(self.url, data)
    #     form = response.context.get('form')
    #     print('\n', form.errors)
    #     # self.client.post(self.url, data)
    #     self.assertTrue(Plan.objects.get(id=1).text == 'changed text')

    # # TODO Nonsense error for field image with null=True, blank=True:
    # # ValueError: The 'image' attribute has no file associated with it.
    # def test_invalid_post_data(self):
    #     self.client.force_login(self.user1)
    #     form = PlansModifyForm(instance=self.plan1)
    #     data = form.initial
    #     data['inform_gm'] = 'Invalid data for BooleanField'
    #     response = self.client.post(self.url, data)
    #     form = response.context.get('form')
    #     # should show the form again, not redirect
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTrue(form.errors)
    #
    # # TODO Nonsense error for field image with null=True, blank=True:
    # # ValueError: The 'image' attribute has no file associated with it.
    # def test_invalid_post_data_empty_fields(self):
    #     self.client.force_login(self.user1)
    #     form = PlansModifyForm(instance=self.plan1)
    #     data = form.initial
    #     data['text'] = ''
    #     response = self.client.post(self.url, data)
    #     form = response.context.get('form')
    #     # should show the form again, not redirect
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTrue(form.errors)
    #     self.assertTrue(Plan.objects.get(id=1).text == 'Demand1')
