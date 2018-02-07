from django.test import TestCase
from django.urls import reverse


class SignupTest(TestCase):
    def setUp(self):
        self.sign_up_url = reverse('account_signup')
        self.user_data = {
            'username': 'jamesbond',
            'password1': 'manofmystery',
            'password2': 'manofmystery'
        }

    def test_home_page(self):
        response = self.client.get('/')
        self.assertContains(response, 'Set goals. Track your progress. Realize your full potential.')
        response = self.client.get(self.sign_up_url)
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        response = self.client.post(self.sign_up_url, self.user_data, follow=True)
        self.assertContains(response, 'Successfully signed in as jamesbond.')
        self.assertContains(response, 'Set a new goal for yourself')



