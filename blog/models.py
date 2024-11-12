from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Custom user model extending AbstractUser to allow future customization."""
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False) # Determines if the user is an admin
    
    def __str__(self):
        return self.username

