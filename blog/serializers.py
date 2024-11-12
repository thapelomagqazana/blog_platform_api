from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from rest_framework import serializers
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, BlogPost

class SignUpSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password validation."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        """Ensure passwords match."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """Create a new user with the validated data."""
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to include user-specific data in the token response.
    """

    def validate(self, attrs):
        """
        Override to include additional fields in the token response.
        """
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
        }
        return data
    
class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for handling password reset requests using the CustomUser model.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Check if the email exists in the CustomUser model.
        """
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError({"email": ["There is no user with this email address."]})
        return value

    def send_reset_email(self):
        """
        Send password reset email with a unique token.
        """
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)
        token_generator = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        send_mail(
            subject="Password Reset Request",
            message=f"Use the link below to reset your password:\n{reset_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset using the CustomUser model.
    """
    new_password = serializers.CharField(write_only=True)
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, data):
        """
        Validate the UID and token, ensuring they correspond to a valid user.
        """
        try:
            user_id = urlsafe_base64_encode(data['uid']).decode()
            user = CustomUser.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError({"uid": "Invalid UID or user not found."})

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        self.user = user
        return data

    def save(self):
        """
        Save the new password for the user.
        """
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()

class AdminSignUpSerializer(serializers.ModelSerializer):
    """
    Serializer for admin sign-up. Validates admin code.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    admin_code = serializers.CharField(write_only=True)  # Admin verification code

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'admin_code']

    def validate_admin_code(self, value):
        """
        Validate the provided admin code.
        """
        if value != "SECRET_ADMIN_CODE":  # Replace with a secure code or verification logic
            raise serializers.ValidationError("Invalid admin code.")
        return value

    def validate(self, data):
        """
        Validate that passwords match.
        """
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """
        Create a new admin user.
        """
        validated_data.pop('password2')
        validated_data.pop('admin_code')
        user = CustomUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            is_admin=True
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class AdminLoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for admin login. Ensures only admins can log in.
    """

    def validate(self, attrs):
        """
        Ensure the user is an admin before issuing tokens.
        """
        data = super().validate(attrs)
        if not self.user.is_admin:
            raise serializers.ValidationError({"error": "You are not authorized to log in as an admin."})
        return data

class BlogPostSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and retrieving blog posts.
    """
    author = serializers.StringRelatedField(read_only=True) # Show the author's username

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def validate_title(self, value):
        """
        Ensure the title is not empty and doesn't contain offensive language.
        """
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if "offensive" in value.lower():
            raise serializers.ValidationError("Title contains prohibited language.")
        return value

    def validate_content(self, value):
        """
        Ensure the content is not too short.
        """
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long.")
        return value
