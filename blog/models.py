from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Custom user model extending AbstractUser to allow future customization."""
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False) # Determines if the user is an admin
    
    def __str__(self):
        return self.username

class BlogPost(models.Model):
    """
    Model representing a blog post
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blog_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

