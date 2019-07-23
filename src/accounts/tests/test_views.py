from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.db.models.query import QuerySet

from addresses.models import Address
from addresses.tests.fixtures import AddressFixtureBilling, AddressFixtureShipping
from billing.models import BillingProfile
from accounts.forms import GuestForm


User = get_user_model()


class SettingsPageViewTestsNotLogged(TestCase):
    def test_redirect_to_login_page_when_not_logged(self):
        resp = self.client.get('/accounts/settings/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/accounts/login/?next_url=/accounts/settings/')
        self.assertRedirects(resp, '/accounts/login/?next_url=/accounts/settings/')


class SettingsPageViewTestsLogged(TestCase):
    def setUp(self):
        self.user_obj = User.objects.create_user(username='test', password='test', email='test@test.pl', is_superuser=False)
        self.client.login(username='test', password='test')

    def test_url_accessible_when_logged_in(self):
        resp = self.client.get('/accounts/settings/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(str(resp.context['user']), 'test')

    def test_url_accessible_by_name_when_logged_in(self):
        resp = self.client.get(reverse('accounts:settings'))
        self.assertEqual(resp.status_code, 200)

    def test_logged_in_uses_correct_template(self):
        resp = self.client.get(reverse('accounts:settings'))
        self.assertTemplateUsed(resp, 'accounts/settings.html')

    def test_context_object_is_username(self):
        resp = self.client.get(reverse('accounts:settings'))
        self.assertEqual(resp.context['object'], self.user_obj)

    def test_context_user_orders(self):
        resp = self.client.get(reverse('accounts:settings'))
        self.assertIsInstance(resp.context['orders'], QuerySet)
        self.assertIsInstance(resp.context['billing_addresses'], QuerySet)
        self.assertIsInstance(resp.context['shipping_addresses'], QuerySet)
        self.assertIsInstance(resp.context['viewed_products'], list)
        self.assertEqual(resp.context['object'], self.user_obj)

    def test_make_address_stale_address_id_exist(self):
        billing_profile_obj, created = BillingProfile.objects.get_or_create(user=self.user_obj, email=self.user_obj.email)
        address_data = AddressFixtureShipping
        address_data['billing_profile'] = billing_profile_obj
        address_obj = Address.objects.create(**address_data)
        self.assertTrue(address_obj.current)
        resp = self.client.post(reverse('accounts:settings'),
                                {'del_address': True,
                                 'address_id': address_obj.id
                                 })
        address_obj.refresh_from_db()
        self.assertFalse(address_obj.current)
        Address.objects.filter(id=address_obj.id).delete()
        BillingProfile.objects.filter(id=billing_profile_obj.id).delete()

    def test_make_address_stale_address_id_not_exist(self):
        resp = self.client.post(reverse('accounts:settings'),
                                {'del_address': True,
                                 'address_id': 666
                                 })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('accounts:settings'))

    def test_make_address_stale_no_address_id_specified(self):
        resp = self.client.post(reverse('accounts:settings'), {'del_address': True})
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('accounts:settings'))

    def tearDown(self):
        User.objects.filter(username='test').delete()
        self.client.logout()


class GuestRegisterView(TestCase):
    def setUp(self):
        self.user_obj = User.objects.create_user(username='test', password='test', email='test@test.pl')

    def test_context_contains_data(self):
        resp = self.client.get(reverse('accounts:guest_register'))
        self.assertTrue(resp.context['title'])
        self.assertTrue(resp.context['button'])

    def test_form_invalid(self):
        data = {'email': 'testtest.pl', 'subscribe': False}
        form = GuestForm(data=data)
        self.assertFalse(form.is_valid())
        resp = self.client.post(reverse('accounts:guest_register'), data)

        messages = list(resp.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level, 30)

    def test_form_valid(self):
        data = {'email': 'test@test.pl', 'subscribe': False}
        form = GuestForm(data=data)
        self.assertTrue(form.is_valid())

    def test_guest_email_id_created(self):
        data = {'email': 'test@test.pl', 'subscribe': False}
        session = self.client.session
        self.assertFalse(session.get('guest_email_id'))
        resp = self.client.post(reverse('accounts:guest_register'), data)
        session = self.client.session
        self.assertTrue(session.get('guest_email_id'))

    def test_redirect(self):
        data = {'email': 'test@test.pl', 'subscribe': False, 'next_url': '/'}
        resp = self.client.post(reverse('accounts:guest_register'), data)
        self.assertRedirects(resp, '/')

    def tearDown(self):
        User.objects.filter(username='test').delete()

