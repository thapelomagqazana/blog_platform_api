from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status, generics, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import BlogPost
from .serializers import (SignUpSerializer, PasswordResetRequestSerializer, 
                          PasswordResetConfirmSerializer, AdminSignUpSerializer, 
                          AdminLoginSerializer, BlogPostSerializer, BlogPostEditSerializer)
from .permissions import IsAuthorPermission

class SignUpView(CreateAPIView):
    """API endpoint for user registration."""
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]  # Ensure anyone can access this endpoint

    def post(self, request, *args, **kwargs):
        """Handle POST request to create a new user."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validates input data
        self.perform_create(serializer)
        return Response(
            {"message": "User created successfully."},
            status=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        """Save the serializer to create the user."""
        serializer.save()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom view for obtaining access and refresh tokens upon user login.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to provide JWT tokens.
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom view for refreshing access tokens using a valid refresh token.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST request to refresh JWT tokens.
        """
        return super().post(request, *args, **kwargs)

class PasswordResetRequestView(APIView):
    """
    Handles password reset requests.
    """

    permission_classes = [AllowAny]  # Ensure this view is accessible without authentication
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_reset_email()
        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Handles password reset confirmation.
    """
    permission_classes = [AllowAny]  # Ensure this view is accessible without authentication
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

class AdminSignUpView(APIView):
    """
    API view for admin sign-up.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle POST request to register a new admin.
        """
        serializer = AdminSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Admin account created successfully."}, status=status.HTTP_201_CREATED)


class AdminLoginView(TokenObtainPairView):
    """
    API view for admin login.
    """
    permission_classes = [AllowAny]
    serializer_class = AdminLoginSerializer

class BlogPostCreateView(generics.CreateAPIView):
    """
    API view for creating a new blog post.
    """
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticated] # Ensures only logged-in users can create blog posts.

    def perform_create(self, serializer):
        """
        Save the blog post with the logged-in user as the author.
        """
        serializer.save(author=self.request.user)

class BlogPostEditView(generics.UpdateAPIView):
    """
    API view for editing a blog post.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostEditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restrict the queryset to posts owned by the authenticated user.
        """
        return BlogPost.objects.filter(author=self.request.user)

class BlogPostDeleteView(generics.DestroyAPIView):
    """
    API view for deleting a blog post.
    """
    queryset = BlogPost.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Restrict the queryset to posts owned by the authenticated user.
        """
        return BlogPost.objects.filter(author=self.request.user)