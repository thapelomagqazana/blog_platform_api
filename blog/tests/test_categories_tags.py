import pytest
from rest_framework.test import APIClient
from ..models import BlogPost, Category, Tag
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    return User.objects.create_user(username='testuser', email='user@example.com', password='password123')

@pytest.fixture
def create_category():
    return Category.objects.create(name='Tech', slug='tech')

@pytest.fixture
def create_tag():
    return Tag.objects.create(name='Django', slug='django')

@pytest.fixture
def create_blog_post(create_user, create_category):
    return BlogPost.objects.create(title="Test Post", content="Content of the test post", author=create_user, category=create_category)

@pytest.mark.django_db
def test_list_categories(api_client, create_category):
    response = api_client.get('/api/categories/')
    assert response.status_code == 200
    assert len(response.data["results"]) == 1

@pytest.mark.django_db
def test_list_tags(api_client, create_tag):
    response = api_client.get('/api/tags/')
    assert response.status_code == 200
    assert len(response.data["results"]) == 1

@pytest.mark.django_db
def test_filter_posts_by_category(api_client, create_blog_post):
    response = api_client.get('/api/posts/?category=tech')
    assert response.status_code == 200
    assert len(response.data["results"]) == 1

@pytest.mark.django_db
def test_filter_posts_by_tag(api_client, create_blog_post, create_tag):
    create_blog_post.tags.add(create_tag)
    response = api_client.get('/api/posts/?tag=django')
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
