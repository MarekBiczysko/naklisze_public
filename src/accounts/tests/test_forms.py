from unittest import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import LoginForm, RegisterForm
from django import forms

User = get_user_model()


class LoginFormTests(TestCase):
    def setUp(self):
        self.good_user = User.objects.create(username='test3', password='test3')

    def test_clean_username(self):
        data = {'username': self.good_user.username, 'password': self.good_user.password}
        form = LoginForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(self.good_user.username, form.clean_username())

    def test_clean_username_no_user(self):
        data = {'username': 'notexist', 'password': self.good_user.password}
        form = LoginForm(data=data)
        self.assertFalse(form.is_valid())
        form.cleaned_data = data
        with self.assertRaises(forms.ValidationError) as e:
            form.clean_username()
        self.assertEqual(e.exception.message, "Niepoprawny użytkownik")

    def tearDown(self):
        User.objects.filter(username='test3').delete()


class RegisterFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test4', password='test4')
        self.user.email = "test4@test.pl"
        self.user.save()

    def test_form_is_valid(self):
        data = {'username': 'test5', 'password': 'test5', 'password2': 'test5', 'email': 'test5@test.pl', 'accept': True}
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(data['username'], form.clean_username())
        self.assertEqual(data['password2'], form.clean_password2())
        self.assertEqual(data['email'], form.clean_email())
        User.objects.filter(username='test5').delete()

    def test_required_accept_button_false(self):
        data = {'username': self.user.username, 'password': self.user.password, 'password2': self.user.password, 'email': 'test55@test.pl', 'accept': False}
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_clean_username_user_exist(self):
        data = {'username': self.user.username, 'password': self.user.password, 'password2': self.user.password, 'email': 'test44@test.pl'}
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        form.cleaned_data = data
        with self.assertRaises(forms.ValidationError) as e:
            form.clean_username()
        self.assertEqual(e.exception.message, "Użytkownik już istnieje")

    def test_clean_password2_mismatch(self):
        data = {'username': 'test6', 'password': 'test6', 'password2': 'test666', 'email': 'test6@test.pl'}
        form = RegisterForm(data=data)
        form.cleaned_data = data
        self.assertFalse(form.is_valid())
        with self.assertRaises(forms.ValidationError) as e:
            form.clean_password2()
        self.assertEqual(e.exception.message, "Niezgodność podanych haseł")

    def test_clean_email_exist(self):
        data = {'username': 'test7', 'password': 'test7', 'password2': 'test7', 'email': self.user.email}
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        form.cleaned_data = data
        with self.assertRaises(forms.ValidationError) as e:
            form.clean_email()
        self.assertEqual(e.exception.message, "Email znajduje się już w bazie")

    def tearDown(self):
        User.objects.filter(username='test4').delete()

