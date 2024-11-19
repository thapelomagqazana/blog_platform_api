from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django_otp.models import Device

class CustomUser(AbstractUser):
    """
    CustomUser extends the default Django AbstractUser to include unique email field and custom relationships for groups and permissions.
    
    Attributes:
        email (EmailField): A unique email address for the user.
        groups (ManyToManyField): A many-to-many relationship with the Group model, allowing custom related name.
        user_permissions (ManyToManyField): A many-to-many relationship with the Permission model, allowing custom related name.
    """
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

class TOTPDevice(Device):
    """
    TOTPDevice extends the base Device model from django-otp to provide two-factor authentication support.
    
    Attributes:
        user (ForeignKey): A reference to the associated CustomUser.
        name (CharField): A unique name for the device, up to 64 characters.
        confirmed (BooleanField): Indicates whether the device is confirmed for use.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='custom_totpdevices')
    name = models.CharField(max_length=64, unique=True)
    confirmed = models.BooleanField(default=False)

class BlogPost(models.Model):
    """
    BlogPost represents a blog entry authored by a CustomUser.
    
    Attributes:
        title (CharField): The title of the blog post, up to 255 characters.
        content (TextField): The main content of the blog post.
        author (ForeignKey): A reference to the CustomUser who authored the post.
        created_at (DateTimeField): The datetime when the post was created. Automatically set on creation.
        updated_at (DateTimeField): The datetime when the post was last updated. Automatically set on update.
        
    Methods:
        __str__(): Returns the string representation of the BlogPost (its title).
        
    Meta:
        ordering: Orders blog posts by creation date in descending order.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    """
    Represents a comment on a blog post. Supports nested comments for replies.
    
    Attributes:
        post (ForeignKey): The blog post this comment belongs to. Uses a reverse relationship named 'comments'.
        author (ForeignKey): The user who authored the comment.
        content (TextField): The text content of the comment.
        parent (ForeignKey): A reference to another comment as the parent, enabling nested comments (replies). Optional.
        created_at (DateTimeField): The date and time when the comment was created. Automatically set on creation.
        updated_at (DateTimeField): The date and time when the comment was last updated. Automatically set on update.
        
    Methods:
        __str__(): Returns a string representation of the comment.
    """
    post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns:
            str: A string representation of the comment, showing the author and the post.
        """
        return f'Comment by {self.author} on {self.post}'