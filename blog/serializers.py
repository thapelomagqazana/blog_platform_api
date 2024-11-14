from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from .models import BlogPost, Category, Tag

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    """Serializer for user signup."""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        """Ensure both passwords match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset."""
    email = serializers.EmailField()

    def validate_email(self, value):
        """Ensure the email belongs to a registered user."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("There is no user registered with this email address.")
        return value
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming and resetting the password."""
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        try:
            uid = smart_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(id=uid)
        except (DjangoUnicodeDecodeError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid UID")

        token = attrs.get('token')
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid or expired token.")

        attrs['user'] = user
        return attrs

    def save(self):
        """Save the new password."""
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for categories.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for tags.
    """
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class BlogPostSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating blog posts.
    Includes nested category and tags.
    """
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'category', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def create(self, validated_data):
        """
        Create a new blog post with category and tags.
        """
        category_data = validated_data.pop('category')
        tags_data = validated_data.pop('tags')
        category, _ = Category.objects.get_or_create(**category_data)
        blog_post = BlogPost.objects.create(category=category, **validated_data)

        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            blog_post.tags.add(tag)

        return blog_post

    def update(self, instance, validated_data):
        """
        Update a blog post and its related category and tags.
        """
        category_data = validated_data.pop('category', None)
        tags_data = validated_data.pop('tags', None)

        if category_data:
            category, _ = Category.objects.get_or_create(**category_data)
            instance.category = category

        if tags_data:
            instance.tags.clear()
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(**tag_data)
                instance.tags.add(tag)

        return super().update(instance, validated_data)

class BlogPostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a single blog post.
    """
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

