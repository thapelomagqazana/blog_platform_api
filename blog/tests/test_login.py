from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

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

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='OldPassword123'
        )
        self.reset_request_url = reverse('password_reset_request')
        self.reset_confirm_url = reverse('password_reset_confirm')

        # Generate valid UID and token
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = PasswordResetTokenGenerator().make_token(self.user)

    def test_password_reset_request_valid_email(self):
        response = self.client.post(self.reset_request_url, {'email': 'testuser@example.com'})
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password reset email sent.')

    def test_password_reset_request_invalid_email(self):
        response = self.client.post(self.reset_request_url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_password_reset_confirm_valid(self):
    #     """
    #     Test password reset confirmation with valid UID and token.
    #     """
    #     response = self.client.post(self.reset_confirm_url, {
    #         'uid': self.uid,
    #         'token': self.token,
    #         'new_password': 'NewPassword123'
    #     })
    #     print(response.data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(self.user.check_password('NewPassword123'))

    def test_password_reset_confirm_invalid_token(self):
        response = self.client.post(self.reset_confirm_url, {
            'uid': 'invalid',
            'token': 'invalidtoken',
            'new_password': 'NewPassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)