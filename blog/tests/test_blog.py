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

class BlogPostEditTests(APITestCase):
    """
    Tests for editing a blog post.
    """

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='StrongPassword123'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='StrongPassword123'
        )
        self.post = BlogPost.objects.create(
            title='Initial Title',
            content='Initial content.',
            author=self.user
        )
        self.edit_url = reverse('post_edit', kwargs={'pk': self.post.pk})
        self.valid_data = {
            'title': 'Updated Title',
            'content': 'Updated content that is more than 10 characters.'
        }
    
    def authenticate_user(self):
        """
        Authenticate the test client using JWT token.
        """
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_edit_post_authenticated_author(self):
        """
        Test that the author can edit their own post.
        """
        self.authenticate_user()
        self.client.login(username='testuser', password='StrongPassword123')
        response = self.client.put(self.edit_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')
        self.assertEqual(self.post.content, 'Updated content that is more than 10 characters.')

    def test_edit_post_unauthenticated(self):
        """
        Test that unauthenticated users cannot edit posts.
        """
        response = self.client.put(self.edit_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_edit_post_invalid_title(self):
        """
        Test that invalid titles are rejected.
        """
        self.authenticate_user()
        self.client.login(username='testuser', password='StrongPassword123')
        response = self.client.put(self.edit_url, {'title': '', 'content': 'Valid content.'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_edit_post_short_content(self):
        """
        Test that content that is too short is rejected.
        """
        self.authenticate_user()
        self.client.login(username='testuser', password='StrongPassword123')
        response = self.client.put(self.edit_url, {'title': 'Valid Title', 'content': 'short'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('content', response.data)

class BlogPostDeleteTests(APITestCase):
    """
    Tests for deleting a blog post.
    """

    def setUp(self):
        """
        Set up test data including a test user and a blog post.
        """
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='StrongPassword123'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='StrongPassword123'
        )
        self.post = BlogPost.objects.create(
            title='My Blog Post',
            content='This is my first post.',
            author=self.user
        )
        self.delete_url = reverse('post_delete', kwargs={'pk': self.post.pk})
    
    def authenticate_user(self):
        """
        Authenticate the test client using JWT token.
        """
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_delete_post_authenticated_author(self):
        """
        Test that the author can delete their own post.
        """
        self.authenticate_user()
        self.client.login(username='testuser', password='StrongPassword123')
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())

    def test_delete_post_unauthenticated(self):
        """
        Test that unauthenticated users cannot delete posts.
        """
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
