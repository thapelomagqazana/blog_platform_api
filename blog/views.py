from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserSignupSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class UserSignupView(generics.CreateAPIView):
    """API view for user signup."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSignupSerializer

class LoginView(APIView):
    """API view for user login."""
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """Handle user login."""
        email = request.data.get('email')
        password = request.data.get('password')
        print(f"Login attempt: email={email}, password={password}")

        user = authenticate(request, username=email, password=password)
        print(f"Authenticated user: {user}")

        if user is not None:
            if not user.is_active:
                return Response({'error': 'Account is inactive.'}, status=status.HTTP_401_UNAUTHORIZED)
            
            refresh = RefreshToken.for_user(user)
            update_last_login(None, user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class PasswordResetView(APIView):
    """View for handling password reset."""
    permission_classes = [AllowAny]

    def post(self, request):
        # Implement password reset here.
        pass  # Replace with logic
