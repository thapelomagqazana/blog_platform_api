from django.urls import path
from .views import SignUpView, CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
