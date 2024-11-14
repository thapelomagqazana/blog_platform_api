import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    """Fixture for DRF API client."""
    return APIClient()

@pytest.fixture
def create_user():
    """Fixture to create a test user."""
    def _create_user(email='testuser@example.com', password='TestPassword123'):
        return User.objects.create_user(
            username='testuser', 
            email=email, 
            password=password,
        )
    return _create_user

@pytest.mark.django_db
class TestUserSignup:
    """Tests for user signup."""

    def test_signup_success(self, api_client):
        """Test successful user signup."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }
        response = api_client.post('/api/signup/', data)
        assert response.status_code == 201
        assert User.objects.filter(email="newuser@example.com").exists()

    def test_signup_password_mismatch(self, api_client):
        """Test signup with mismatched passwords."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password2": "MismatchPassword123!",
        }
        response = api_client.post('/api/signup/', data)
        assert response.status_code == 400
        assert "password" in response.data

    def test_signup_duplicate_email(self, api_client, create_user):
        """Test signup with duplicate email."""
        create_user(email="duplicate@example.com")
        data = {
            "username": "newuser2",
            "email": "duplicate@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }
        response = api_client.post('/api/signup/', data)
        assert response.status_code == 400
        assert "email" in response.data

    def test_signup_weak_password(self, api_client):
        """Test signup with weak password."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "123",
            "password2": "123",
        }
        response = api_client.post('/api/signup/', data)
        assert response.status_code == 400
        assert "password" in response.data

@pytest.mark.django_db
class TestUserLogin:
    """Tests for user login."""

    def test_login_success(self, api_client, create_user):
        """Test successful login."""
        create_user()
        data = {"email": "testuser@example.com", "password": "TestPassword123"}
        response = api_client.post('/api/login/', data)
        print(response.data)
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials."""
        data = {"email": "wronguser@example.com", "password": "WrongPassword123"}
        response = api_client.post('/api/login/', data)
        assert response.status_code == 401
        assert "error" in response.data

    def test_login_inactive_user(self, api_client, create_user):
        """Test login for inactive user."""
        user = create_user()
        user.is_active = False
        user.save()
        data = {"email": "testuser@example.com", "password": "TestPassword123"}
        response = api_client.post('/api/login/', data)
        assert response.status_code == 401
        assert "error" in response.data

