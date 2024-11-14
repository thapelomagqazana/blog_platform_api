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
def create_other_user():
    return User.objects.create_user(username='otheruser', email='other@example.com', password='password123')

@pytest.fixture
def create_blog_post(create_user):
    return BlogPost.objects.create(title="Test Post", content="Content of the test post", author=create_user)

@pytest.mark.django_db
def test_create_post(api_client, create_user):
    """Test successful creation of a blog post."""
    api_client.force_authenticate(user=create_user)

    # Create a category and tag
    category_data = {"name": "Tech", "slug": "tech"}
    tag_data = [{"name": "Django", "slug": "django"}]

    # Include category and tags in the request data
    data = {
        "title": "New Post",
        "content": "This is a new post",
        "category": category_data,
        "tags": tag_data
    }

    # Set format='json' to ensure correct content type
    response = api_client.post('/api/posts/create/', data, format='json')
    print(response.data)
    assert response.status_code == 201
    assert response.data['title'] == data['title']
    assert response.data['content'] == data['content']
    assert response.data['author'] == create_user.id

@pytest.mark.django_db
def test_create_post_unauthenticated(api_client):
    """Test creating a blog post without authentication."""
    data = {"title": "New Post", "content": "This is a new post"}
    response = api_client.post('/api/posts/create/', data)
    assert response.status_code == 401  # Unauthorized

@pytest.mark.django_db
def test_update_post(api_client, create_user, create_blog_post):
    """Test updating a blog post by the author."""
    api_client.force_authenticate(user=create_user)
    data = {"title": "Updated Post"}
    response = api_client.patch(f'/api/posts/{create_blog_post.id}/edit/', data)
    assert response.status_code == 200
    assert response.data['title'] == data['title']

@pytest.mark.django_db
def test_update_post_unauthorized(api_client, create_other_user, create_blog_post):
    """Test updating a blog post by a non-author."""
    api_client.force_authenticate(user=create_other_user)
    data = {"title": "Unauthorized Update"}
    response = api_client.patch(f'/api/posts/{create_blog_post.id}/edit/', data)
    assert response.status_code == 403  # Forbidden

@pytest.mark.django_db
def test_update_post_unauthenticated(api_client, create_blog_post):
    """Test updating a blog post without authentication."""
    data = {"title": "Unauthorized Update"}
    response = api_client.patch(f'/api/posts/{create_blog_post.id}/edit/', data)
    assert response.status_code == 401  # Unauthorized

@pytest.mark.django_db
def test_delete_post(api_client, create_user, create_blog_post):
    """Test deleting a blog post by the author."""
    api_client.force_authenticate(user=create_user)
    response = api_client.delete(f'/api/posts/{create_blog_post.id}/delete/')
    assert response.status_code == 204

@pytest.mark.django_db
def test_delete_post_unauthorized(api_client, create_other_user, create_blog_post):
    """Test deleting a blog post by a non-author."""
    api_client.force_authenticate(user=create_other_user)
    response = api_client.delete(f'/api/posts/{create_blog_post.id}/delete/')
    assert response.status_code == 403  # Forbidden

@pytest.mark.django_db
def test_delete_post_unauthenticated(api_client, create_blog_post):
    """Test deleting a blog post without authentication."""
    response = api_client.delete(f'/api/posts/{create_blog_post.id}/delete/')
    assert response.status_code == 401  # Unauthorized

@pytest.mark.django_db
def test_list_posts(api_client, create_blog_post):
    """Test listing all blog posts."""
    response = api_client.get('/api/posts/')
    assert response.status_code == 200
    assert len(response.data) > 0

@pytest.mark.django_db
def test_view_post_detail(api_client, create_blog_post):
    """Test retrieving a specific blog post's details."""
    response = api_client.get(f'/api/posts/{create_blog_post.id}/')
    assert response.status_code == 200
    assert response.data['title'] == create_blog_post.title
    assert response.data['content'] == create_blog_post.content

@pytest.mark.django_db
def test_view_nonexistent_post_detail(api_client):
    """Test retrieving a blog post that does not exist."""
    response = api_client.get('/api/posts/9999/')
    assert response.status_code == 404  # Not Found
