from unittest import TestCase
from django.contrib.auth import get_user_model
from accounts.models import GuestEmail
from accounts.tokens import TokenGenerator


User = get_user_model()


class ModelsGuestEmailPrint(TestCase):
    def setUp(self):
        self.guest_email_obj = GuestEmail.objects.create(email='test1@test.pl')

    def test_email_print(self):
        self.assertIsInstance(self.guest_email_obj, GuestEmail)
        self.assertEqual(str(self.guest_email_obj), str(self.guest_email_obj.email))

    def tearDown(self):
        GuestEmail.objects.filter(email='test1@test.pl').delete()


class TokensTokenGenerator(TestCase):
    def setUp(self):
        self.user_obj = User.objects.create(username='test2', password='test2', is_active=True)

    def test__make_hash_value(self):
        token = TokenGenerator()
        result = token._make_hash_value(self.user_obj, self.user_obj.date_joined)
        string_add = str(self.user_obj.pk) + str(self.user_obj.date_joined) + str(self.user_obj.is_active)
        self.assertEqual(result, string_add)

    def tearDown(self):
        User.objects.filter(username='test2').delete()
