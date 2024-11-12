from django.urls import path
from .views import SignUpView, CustomTokenObtainPairView, CustomTokenRefreshView, PasswordResetRequestView, PasswordResetConfirmView, AdminSignUpView, AdminLoginView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('admin/signup/', AdminSignUpView.as_view(), name='admin_signup'),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),

]
