import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from ..models import BlogPost, Comment

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    return User.objects.create_user(username='testuser', email='user@example.com', password='password123')

@pytest.fixture
def create_post(create_user):
    return BlogPost.objects.create(title='Test Post', content='Test Content', author=create_user)

@pytest.fixture
def create_comment(create_user, create_post):
    return Comment.objects.create(post=create_post, author=create_user, content='Test Comment')

@pytest.mark.django_db
def test_create_comment(api_client, create_user, create_post):
    api_client.force_authenticate(user=create_user)
    data = {"content": "New Comment", "post": create_post.id}
    response = api_client.post(f'/api/posts/{create_post.id}/comments/', data, format='json')
    assert response.status_code == 201

@pytest.mark.django_db
def test_reply_to_comment(api_client, create_user, create_post, create_comment):
    api_client.force_authenticate(user=create_user)
    data = {"content": "Reply to Comment", "post": create_post.id, "parent": create_comment.id}
    response = api_client.post(f'/api/posts/{create_post.id}/comments/', data, format='json')
    assert response.status_code == 201

@pytest.mark.django_db
def test_delete_comment(api_client, create_user, create_comment):
    api_client.force_authenticate(user=create_user)
    response = api_client.delete(f'/api/comments/{create_comment.id}/delete/')
    assert response.status_code == 204

@pytest.mark.django_db
def test_delete_comment_unauthorized(api_client, create_user, create_comment):
    other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='password123')
    api_client.force_authenticate(user=other_user)
    response = api_client.delete(f'/api/comments/{create_comment.id}/delete/')
    assert response.status_code == 403
