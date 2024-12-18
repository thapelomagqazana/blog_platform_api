from rest_framework import generics, status, views
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django_rest_passwordreset.views import ResetPasswordRequestToken, ResetPasswordConfirm
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.core.cache import cache
from .utils import send_notification
from .models import (BlogPost, Comment, Like, 
                     PostView, Notification, NotificationPreference)
from .serializers import (UserSerializer, LoginSerializer, TOTPDeviceSerializer, 
                          BlogPostSerializer, CommentSerializer,
                           LikeSerializer, PostViewSerializer,
                           NotificationSerializer, NotificationPreferenceSerializer)

class RegisterView(generics.CreateAPIView):
    """
    View to handle user registration.
    
    Attributes:
        queryset: All user instances.
        serializer_class: Serializer used for user creation.
        permission_classes: Allows public access.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class LoginView(views.APIView):
    """
    View to handle user login and provide JWT tokens.
    
    Methods:
        post(request): Authenticates user and returns JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Authenticates the user and provides access and refresh tokens.
        
        Args:
            request: HTTP request containing username and password.
            
        Returns:
            Response: JWT tokens if credentials are valid; otherwise, an error response.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(views.APIView):
    """
    View to handle user logout by blacklisting the refresh token.
    
    Methods:
        post(request): Blacklists the provided refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Blacklists the provided refresh token to log the user out.
        
        Args:
            request: HTTP request containing the refresh token.
            
        Returns:
            Response: Success or error response based on the provided token.
        """
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(ResetPasswordRequestToken):
    """
    View to request a password reset token.
    
    Permissions:
        Public access.
    """
    permission_classes = [AllowAny]

class PasswordResetConfirmView(ResetPasswordConfirm):
    """
    View to confirm a password reset using the provided token.
    
    Permissions:
        Public access.
    """
    permission_classes = [AllowAny]

class TOTPDeviceView(generics.ListCreateAPIView):
    """
    View to list and create TOTP devices for two-factor authentication.
    
    Attributes:
        queryset: All TOTP devices.
        serializer_class: Serializer for TOTP devices.
        permission_classes: Allows access to authenticated users only.
        
    Methods:
        perform_create(serializer): Associates the created TOTP device with the current user.
    """
    queryset = TOTPDevice.objects.all()
    serializer_class = TOTPDeviceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Saves the TOTP device with the current user.
        
        Args:
            serializer: TOTPDeviceSerializer instance.
        """
        serializer.save(user=self.request.user)

class BlogPostPagination(PageNumberPagination):
    """
    Custom pagination for blog posts.
    
    Attributes:
        page_size: Number of items per page.
    """
    page_size = 10

class BlogPostListCreateView(generics.ListCreateAPIView):
    """
    View to list and create blog posts.
    
    Attributes:
        queryset: All blog posts.
        serializer_class: Serializer for blog posts.
        permission_classes: Allows read access to all users and write access to authenticated users.
        pagination_class: Uses custom pagination for blog posts.
        
    Methods:
        get_queryset(): Returns cached blog posts if available, otherwise fetches from the database.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = BlogPostPagination

    def get_queryset(self):
        """
        Retrieves blog posts from cache or database.
        
        Returns:
            QuerySet: List of blog posts.
        """
        queryset = cache.get('blog_posts')
        if not queryset:
            queryset = BlogPost.objects.all()
            cache.set('blog_posts', queryset, timeout=60*15)  # Cache for 15 minutes
        return queryset

class BlogPostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a single blog post.
    
    Attributes:
        queryset: All blog posts.
        serializer_class: Serializer for blog posts.
        permission_classes: Allows read access to all users and write access to authenticated users.
        
    Methods:
        get_object(): Retrieves a blog post from cache or database.
        perform_update(serializer): Updates the blog post and refreshes the cache.
        perform_destroy(instance): Deletes the blog post and clears the cache.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        """
        Retrieves the blog post from cache or database.
        
        Returns:
            BlogPost: The requested blog post instance.
        """
        obj = cache.get(f'blog_post_{self.kwargs["pk"]}')
        if not obj:
            obj = super().get_object()
            cache.set(f'blog_post_{self.kwargs["pk"]}', obj, timeout=60*15)  # Cache for 15 minutes
        return obj

    def perform_update(self, serializer):
        """
        Updates the blog post and refreshes the cache.
        
        Args:
            serializer: BlogPostSerializer instance.
        """
        instance = serializer.save()
        cache.set(f'blog_post_{instance.pk}', instance, timeout=60*15)
        cache.delete('blog_posts')

    def perform_destroy(self, instance):
        """
        Deletes the blog post and clears the cache.
        
        Args:
            instance: BlogPost instance to be deleted.
        """
        cache.delete(f'blog_post_{instance.pk}')
        cache.delete('blog_posts')
        instance.delete()

class CommentListCreateView(generics.ListCreateAPIView):
    """
    View to list all comments or create a new comment.
    
    Attributes:
        queryset: Retrieves all comment instances.
        serializer_class: Serializer used for serializing and deserializing comment data.
        permission_classes: Allows read access to all users and write access to authenticated users.
        
    Methods:
        perform_create(serializer): Associates the newly created comment with the currently authenticated user.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """
        Saves the comment with the currently authenticated user as the author.
        
        Args:
            serializer (CommentSerializer): Serializer instance for the comment.
        """
        comment = serializer.save(author=self.request.user)
        send_notification(comment.post.author, f'New comment on your post: {comment.content}')

class CommentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific comment.
    
    Attributes:
        queryset: Retrieves all comment instances.
        serializer_class: Serializer used for serializing and deserializing comment data.
        permission_classes: Allows read access to all users and write access to authenticated users.
        
    Methods:
        perform_update(serializer): Updates the comment while preserving the original author.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        """
        Updates the comment with the same author.
        
        Args:
            serializer (CommentSerializer): Serializer instance for the comment.
        """
        serializer.save(author=self.request.user)

class LikePostView(generics.CreateAPIView):
    """
    View to handle liking a blog post.
    
    Attributes:
        queryset: Retrieves all like instances.
        serializer_class: Serializer used for creating a like.
        permission_classes: Allows access to authenticated users only.
        
    Methods:
        post(request, *args, **kwargs): Handles the creation of a like for a blog post, ensuring a user can like a post only once.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to like a blog post.
        
        Args:
            request: HTTP request containing user and post data.
            
        Returns:
            Response: Success message if like is created, or error if the post is already liked.
        """
        post_id = self.kwargs['pk']
        user = request.user
        post = BlogPost.objects.get(pk=post_id)
        if Like.objects.filter(user=user, post=post).exists():
            return Response({"detail": "You have already liked this post."}, status=status.HTTP_400_BAD_REQUEST)
        Like.objects.create(user=user, post=post)
        return Response({"detail": "Post liked."}, status=status.HTTP_201_CREATED)

class UnlikePostView(generics.DestroyAPIView):
    """
    View to handle unliking a blog post.
    
    Attributes:
        queryset: Retrieves all like instances.
        serializer_class: Serializer used for deleting a like.
        permission_classes: Allows access to authenticated users only.
        
    Methods:
        delete(request, *args, **kwargs): Handles the deletion of a like for a blog post, ensuring a user can only unlike posts they have liked.
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        """
        Handles the DELETE request to unlike a blog post.
        
        Args:
            request: HTTP request containing user and post data.
            
        Returns:
            Response: Success message if like is deleted, or error if the post was not liked.
        """
        post_id = self.kwargs['pk']
        user = request.user
        post = BlogPost.objects.get(pk=post_id)
        like = Like.objects.filter(user=user, post=post).first()
        if like:
            like.delete()
            return Response({"detail": "Post unliked."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "You have not liked this post."}, status=status.HTTP_400_BAD_REQUEST)
    
class AnalyticsView(generics.GenericAPIView):
    """
    View to provide analytics data about the application, including users, posts, comments, likes, and views.
    
    Attributes:
        permission_classes: Restricts access to admin users only.
        
    Methods:
        get(request, *args, **kwargs): Retrieves aggregated analytics data and returns it in the response.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        """
        Handles the GET request to retrieve analytics data.
        
        Args:
            request: HTTP request.
            
        Returns:
            Response: Aggregated analytics data including counts of active users, posts, comments, likes, and views.
        """
        active_users = get_user_model().objects.filter(is_active=True).count()
        total_posts = BlogPost.objects.count()
        total_comments = Comment.objects.count()
        total_likes = Like.objects.count()
        total_views = PostView.objects.count()
        data = {
            "active_users": active_users,
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_likes": total_likes,
            "total_views": total_views,
        }
        return Response(data, status=status.HTTP_200_OK)

class NotificationListView(generics.ListAPIView):
    """
    View to list all notifications for the currently authenticated user.

    Attributes:
        serializer_class (NotificationSerializer): Serializer used for serializing notification data.
        permission_classes: Allows access to authenticated users only.

    Methods:
        get_queryset(): Returns the list of notifications for the current user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the notifications for the authenticated user.

        Returns:
            QuerySet: List of notifications for the current user.
        """
        return Notification.objects.filter(user=self.request.user)


class MarkNotificationAsReadView(generics.UpdateAPIView):
    """
    View to mark a notification as read.

    Attributes:
        serializer_class (NotificationSerializer): Serializer used for updating notification data.
        permission_classes: Allows access to authenticated users only.

    Methods:
        get_queryset(): Returns the notifications for the current user.
        perform_update(serializer): Marks the notification as read and saves the instance.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the notifications for the authenticated user.

        Returns:
            QuerySet: List of notifications for the current user.
        """
        return Notification.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        """
        Marks the notification as read and saves the instance.

        Args:
            serializer (NotificationSerializer): Serializer instance for the notification.
        """
        serializer.instance.is_read = True
        serializer.save()


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve or update the notification preferences for the currently authenticated user.

    Attributes:
        serializer_class (NotificationPreferenceSerializer): Serializer used for serializing and updating notification preference data.
        permission_classes: Allows access to authenticated users only.

    Methods:
        get_object(): Returns the notification preferences for the current user.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieves the notification preferences for the authenticated user.

        Returns:
            NotificationPreference: Notification preferences for the current user.
        """
        return self.request.user.notification_preference