from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.db.models.query import QuerySet

User = get_user_model()


# Create your tests here.
class SettingsPageViewTestsLogged(TestCase):
    def setUp(self):
        self.user_obj = User.objects.create_user(username='test', password='test', email='test@test.pl')

    def test_get_viewed_products_unique(self):
        pass

    def test_get_viewed_products_not_unique(self):
        pass

    def test_get_viewed_products_with_not_existing_products(self):
        pass

    def test_get_viewed_products_chronology(self):
        pass

    def test_get_viewed_products_empty_list(self):
        pass


    def tearDown(self):
        User.objects.filter(username='test').delete()

