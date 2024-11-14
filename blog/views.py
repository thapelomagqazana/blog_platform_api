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
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import BlogPost, Category, Tag
from .serializers import (PasswordResetRequestSerializer, PasswordResetConfirmSerializer, 
                          BlogPostSerializer, BlogPostDetailSerializer,
                            CategorySerializer, TagSerializer)

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
    
class CategoryListView(generics.ListAPIView):
    """
    View for listing all categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class TagListView(generics.ListAPIView):
    """
    View for listing all tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    
class BlogPostListView(generics.ListAPIView):
    """
    View for listing blog posts with optional filtering by category or tag.
    """
    serializer_class = BlogPostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Optionally filter blog posts by category or tag.
        """
        queryset = BlogPost.objects.all().order_by("-created_at")
        category_slug = self.request.query_params.get('category')
        tag_slug = self.request.query_params.get('tag')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        return queryset

class BlogPostDetailView(generics.RetrieveAPIView):
    """
    View for retrieving a specific blog post by ID.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostDetailSerializer
    permission_classes = [AllowAny]

class BlogPostCreateView(generics.CreateAPIView):
    """
    View for creating a new blog post.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Add the current logged-in user as the author of the blog post."""
        serializer.save(author=self.request.user)

class BlogPostUpdateView(generics.UpdateAPIView):
    """
    View for updating an existing blog post.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        """
        Ensure only the author can update the post.
        """
        post = self.get_object()
        if post.author != self.request.user:
            raise PermissionDenied("You do not have permission to edit this post.")
        serializer.save(author=self.request.user)

class BlogPostDeleteView(generics.DestroyAPIView):
    """
    View for deleting an existing blog post.
    """
    queryset = BlogPost.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        """
        Ensure only the author can delete the post.
        """
        if instance.author != self.request.user:
            raise PermissionDenied("You do not have permission to delete this post.")
        instance.delete()