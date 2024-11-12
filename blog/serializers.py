from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser

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