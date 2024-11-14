import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from ..models import BlogPost

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    return User.objects.create_user(username='testuser', email='user@example.com', password='password123')

@pytest.fixture
def create_blog_post(create_user):
    return BlogPost.objects.create(title="Test Post", content="Content of the test post", author=create_user)

@pytest.mark.django_db
def test_create_post(api_client, create_user):
    api_client.force_authenticate(user=create_user)
    data = {"title": "New Post", "content": "This is a new post"}
    response = api_client.post('/api/posts/create/', data)
    assert response.status_code == 201

@pytest.mark.django_db
def test_update_post(api_client, create_user, create_blog_post):
    api_client.force_authenticate(user=create_user)
    data = {"title": "Updated Post"}
    response = api_client.patch(f'/api/posts/{create_blog_post.id}/edit/', data)
    assert response.status_code == 200

@pytest.mark.django_db
def test_delete_post(api_client, create_user, create_blog_post):
    api_client.force_authenticate(user=create_user)
    response = api_client.delete(f'/api/posts/{create_blog_post.id}/delete/')
    assert response.status_code == 204

@pytest.mark.django_db
def test_list_posts(api_client, create_blog_post):
    response = api_client.get('/api/posts/')
    assert response.status_code == 200
    assert len(response.data) > 0

@pytest.mark.django_db
def test_view_post_detail(api_client, create_blog_post):
    response = api_client.get(f'/api/posts/{create_blog_post.id}/')
    assert response.status_code == 200
