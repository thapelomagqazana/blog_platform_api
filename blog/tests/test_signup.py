from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

CustomUser = get_user_model()

class SignUpViewTests(APITestCase):
    """Test cases for the SignUp API endpoint."""

    def setUp(self):
        """Set up reusable test data."""
        self.valid_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!"
        }
        self.invalid_email_data = {
            "username": "testuser2",
            "email": "invalid-email",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!"
        }
        self.mismatched_passwords_data = {
            "username": "testuser3",
            "email": "testuser3@example.com",
            "password": "StrongPassword123!",
            "password2": "DifferentPassword123!"
        }
        self.weak_password_data = {
            "username": "testuser4",
            "email": "testuser4@example.com",
            "password": "123",
            "password2": "123"
        }
        self.missing_field_data = {
            "username": "",
            "email": "testuser5@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!"
        }
        self.existing_user_data = {
            "username": "existinguser",
            "email": "existinguser@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!"
        }
        # Create a user to test duplicate data
        CustomUser.objects.create_user(
            username="existinguser", 
            email="existinguser@example.com", 
            password="StrongPassword123!"
        )

    def test_valid_signup(self):
        """Test signing up with valid data."""
        response = self.client.post(reverse('signup'), self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2)  # One user exists from setup
        self.assertEqual(CustomUser.objects.last().email, "testuser@example.com")

    def test_invalid_email_signup(self):
        """Test signing up with an invalid email format."""
        response = self.client.post(reverse('signup'), self.invalid_email_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_mismatched_passwords(self):
        """Test signing up with mismatched passwords."""
        response = self.client.post(reverse('signup'), self.mismatched_passwords_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_weak_password(self):
        """Test signing up with a weak password."""
        response = self.client.post(reverse('signup'), self.weak_password_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_missing_required_fields(self):
        """Test signing up with missing required fields."""
        response = self.client.post(reverse('signup'), self.missing_field_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_duplicate_username(self):
        """Test signing up with an existing username."""
        response = self.client.post(reverse('signup'), self.existing_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_duplicate_email(self):
        """Test signing up with an existing email."""
        duplicate_email_data = {
            "username": "newuser",
            "email": "existinguser@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!"
        }
        response = self.client.post(reverse('signup'), duplicate_email_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)