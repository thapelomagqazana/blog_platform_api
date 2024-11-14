from django.urls import path
from .views import (UserSignupView, LoginView, PasswordResetRequestView,
                     PasswordResetConfirmView, BlogPostListView, BlogPostDetailView,
                     BlogPostCreateView, BlogPostUpdateView, BlogPostDeleteView)

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('posts/', BlogPostListView.as_view(), name='post_list'),
    path('posts/<int:pk>/', BlogPostDetailView.as_view(), name='post_detail'),
    path('posts/create/', BlogPostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', BlogPostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', BlogPostDeleteView.as_view(), name='post_delete'),
]