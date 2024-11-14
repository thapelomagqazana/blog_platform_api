from django.urls import path
from .views import UserSignupView, LoginView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]