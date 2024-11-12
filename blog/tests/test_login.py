from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

CustomUser = get_user_model()


class LoginTests(APITestCase):
    """
    Test cases for user login and JWT token handling.
    """

    def setUp(self):
        """Set up a test user."""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='StrongPassword123!',
            email='testuser@example.com'
        )
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_valid_login(self):
        """Test login with valid credentials."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'StrongPassword123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_login(self):
        """Test login with invalid credentials."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_token_refresh(self):
        """Test token refresh with valid refresh token."""
        login_response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'StrongPassword123!'
        })
        refresh_token = login_response.data['refresh']
        response = self.client.post(self.refresh_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_token_refresh(self):
        """Test token refresh with invalid refresh token."""
        response = self.client.post(self.refresh_url, {'refresh': 'invalidtoken'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)