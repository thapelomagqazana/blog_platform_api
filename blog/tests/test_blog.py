from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import BlogPost

CustomUser = get_user_model()

class BlogPostCreateTests(APITestCase):
    """Tests for creating a new blog post."""

    def setUp(self):
        """
        Set up test data including a test user.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='StrongPassword123'
        )
        self.create_url = reverse('post_create')
        self.valid_data = {
            "title": "My First Blog Post",
            "content": "This is the content of my first blog post."
        }
    
    def authenticate_user(self):
        """
        Authenticate the test client using JWT token.
        """
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_create_post_authenticated(self):
        """
        Test creating a post as an authenticated user.
        """
        self.authenticate_user()  # Authenticate the client
        self.client.login(username='testuser', password='StrongPassword123')
        response = self.client.post(self.create_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BlogPost.objects.count(), 1)
        self.assertEqual(BlogPost.objects.first().author, self.user)
    
    def test_create_post_unauthenticated(self):
        """
        Test that unauthenticated users cannot create posts.
        """
        response = self.client.post(self.create_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_empty_title(self):
        """
        Test creating a post with an empty title.
        """
        self.authenticate_user()
        self.client.login(username='testuser', password='StrongPassword123')
        response = self.client.post(self.create_url, {"title": "", "content": "Valid content."})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_post_short_content(self):
        """
        Test creating a post with content that is too short.
        """
        self.authenticate_user()
        self.client.login(username='testuser', password='StrongPassword123')
        response = self.client.post(self.create_url, {"title": "Valid Title", "content": "short"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)
