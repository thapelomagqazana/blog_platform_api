from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserSignupSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer

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

class PasswordResetRequestView(APIView):
    """View for handling password reset."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            token = PasswordResetTokenGenerator().make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            reset_link = f"http://example.com/reset-password/{uidb64}/{token}/"  # Modify this link for your frontend

            # Send the email
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_link}",
                from_email="noreply@example.com",
                recipient_list=[email],
            )

            return Response({'message': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmView(APIView):
    """View for handling password reset confirmation."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)