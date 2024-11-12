from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import SignUpSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer

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