from django.test import TestCase
from django.contrib.auth.models import User
from .forms import RegistrationForm
from django.test import Client
from .models import Website
from app.utils import crawl_web
# Create your tests here.


class registrationTest(TestCase):
    # create account for test
    def setUp(self):
        User.objects.create_user(
            'testcase@example.com', 'testcase@example.com', 'matkhau123')

    # Test: email address exists
    def test_registration_form_unique_email(self):
        form = RegistrationForm(data={
            'email': 'testcase@example.com',
            'first_name': 'Phạm',
            'last_name': 'Duy',
            'password1': 'testcase123',
            'password2': 'testcase123'
        })
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['email'], [
            "Email address already exists."])

    # Test: password is too similar to the email address
    def test_registration_form_smiilar_email(self):
        form = RegistrationForm(data={
            'email': 'testcase2@example.com',
            'first_name': 'Phạm',
            'last_name': 'Duy',
            'password1': 'testcase123',
            'password2': 'testcase123',
        })
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['password2'], [
                         "The password is too similar to the email address."])

    # Test: lenght password < 8
    def test_registration_form_too_short(self):
        form = RegistrationForm(data={
            'email': 'testcase2@example.com',
            'first_name': 'Phạm',
            'last_name': 'Duy',
            'password1': 'ithon8',
            'password2': 'ithon8',
        })
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['password2'], [
                         "This password is too short. It must contain at least 8 characters."])

    # Test: password is too common
    def test_registration_form_too_common(self):
        form = RegistrationForm(data={
            'email': 'testcase2@example.com',
            'first_name': 'Phạm',
            'last_name': 'Duy',
            'password1': 'password',
            'password2': 'password',
        })
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['password2'], [
                         "This password is too common."])

    # Test: valid email
    def test_registration_form_isValid_email(self):
        form = RegistrationForm(data={
            'email': 'test',
            'first_name': 'Phạm',
            'last_name': 'Duy',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.failIf(form.is_valid())
        self.assertEqual(form.errors['email'], [
                         "Enter a valid email address."])

    # Test: registration successfully
    def test_registration_form_valid(self):
        form = RegistrationForm(data={
            'email': 'duytien2401@gmail.com',
            'first_name': 'Phạm',
            'last_name': 'Duy',
            'password1': 'testcase123',
            'password2': 'testcase123'})
        self.assertTrue(form.is_valid())


class login_logoutTest(TestCase):
    # create account for test
    def setUp(self):
        User.objects.create_user(
            'testcase@example.com', 'testcase@example.com', 'matkhau123')

    # Test: login successfully
    def test_login_sucess(self):
        c = Client()
        res = c.login(username='testcase@example.com', password='matkhau123')
        self.assertTrue(res)

    # Test: login failed
    def test_login_fail(self):
        c = Client()
        res = c.login(username='testcase@example.com', password='matkhau321')
        self.assertFalse(res)

    # Test: logout
    def test_logout(self):
        c = Client()
        c.login(username='testcase@example.com', password='matkhau123')
        response = c.get('/logout/')
        self.assertEqual(response.status_code, 302)


class crawl_website(TestCase):
    def test_crawl(self):
        # setup
        try:
            website = Website(name="tiki", uri="https://tiki.vn/dien-thoai-may-tinh-bang")
            website.save()
        except KeyError as key_error:
            self.stderr.write(self.style.ERROR(f'Missing Key: "{key_error}"'))
    # Test crawl website
        source = crawl_web(website.id)
        self.assertEqual(len(source) > 1, True)
