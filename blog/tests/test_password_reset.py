import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    """Fixture for DRF API client."""
    return APIClient()

@pytest.fixture
def create_user():
    """Fixture to create a test user."""
    def _create_user(email='testuser@example.com', password='TestPassword123'):
        return User.objects.create_user(username='testuser', email=email, password=password)
    return _create_user

@pytest.mark.django_db
class TestPasswordResetRequest:
    """Tests for password reset request."""

    def test_password_reset_request_success(self, api_client, create_user):
        """Test successful password reset request."""
        user = create_user()
        data = {"email": user.email}
        response = api_client.post('/api/password-reset/', data)
        
        # Assert the response
        assert response.status_code == 200
        assert response.data['message'] == 'Password reset link has been sent to your email.'

        # Check if email was sent
        assert len(mail.outbox) == 1
        assert user.email in mail.outbox[0].to
        assert 'Password Reset Request' in mail.outbox[0].subject

    def test_password_reset_request_invalid_email(self, api_client):
        """Test password reset request with invalid email."""
        data = {"email": "nonexistent@example.com"}
        response = api_client.post('/api/password-reset/', data)
        
        # Assert the response
        assert response.status_code == 400
        assert 'email' in response.data

@pytest.mark.django_db
class TestPasswordResetConfirm:
    """Tests for password reset confirmation."""

    def test_password_reset_confirm_success(self, api_client, create_user):
        """Test successful password reset confirmation."""
        user = create_user()
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        data = {
            "uidb64": uidb64,
            "token": token,
            "new_password": "NewStrongPassword123!"
        }
        response = api_client.post('/api/password-reset-confirm/', data)
        
        # Assert the response
        assert response.status_code == 200
        assert response.data['message'] == 'Password has been reset successfully.'

        # Ensure the password has been updated
        user.refresh_from_db()
        assert user.check_password(data['new_password'])

    def test_password_reset_confirm_invalid_uid(self, api_client):
        """Test password reset confirmation with invalid UID."""
        data = {
            "uidb64": "invaliduid",
            "token": "sometoken",
            "new_password": "NewStrongPassword123!"
        }
        response = api_client.post('/api/password-reset-confirm/', data)
        
        # Assert the response
        assert response.status_code == 400
        assert 'Invalid UID' in str(response.data)

    def test_password_reset_confirm_invalid_token(self, api_client, create_user):
        """Test password reset confirmation with invalid token."""
        user = create_user()
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        data = {
            "uidb64": uidb64,
            "token": "invalidtoken",
            "new_password": "NewStrongPassword123!"
        }
        response = api_client.post('/api/password-reset-confirm/', data)
        
        # Assert the response
        assert response.status_code == 400
        assert 'Invalid or expired token' in str(response.data)
