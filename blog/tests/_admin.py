from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

CustomUser = get_user_model()

class AdminAuthTests(APITestCase):
    """
    Tests for admin sign-up and login.
    """

    def setUp(self):
        self.signup_url = reverse('admin_signup')
        self.login_url = reverse('admin_login')
        self.admin_user = CustomUser.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='StrongPassword123',
            is_admin=True
        )

    def test_admin_signup_valid(self):
        """
        Test admin sign-up with valid data.
        """
        data = {
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
            "admin_code": "SECRET_ADMIN_CODE"  # Must match your validation logic
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_signup_invalid_admin_code(self):
        """
        Test admin sign-up with invalid admin code.
        """
        data = {
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
            "admin_code": "WRONG_CODE"
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_admin_login_valid(self):
        """
        Test admin login with valid credentials.
        """
        data = {
            "username": "adminuser",
            "password": "StrongPassword123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_admin_login_invalid(self):
        """
        Test admin login with non-admin credentials.
        """
        non_admin_user = CustomUser.objects.create_user(
            username='regularuser',
            email='user@example.com',
            password='StrongPassword123'
        )
        data = {
            "username": "regularuser",
            "password": "StrongPassword123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

