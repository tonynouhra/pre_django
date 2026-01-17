from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserProfileView

urlpatterns = [
    # Registration
    path('register/', RegisterView.as_view(), name='register'),

    # Login (get tokens)
    path('login/', TokenObtainPairView.as_view(), name='login'),

    # Refresh token
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User profile
    path('profile/', UserProfileView.as_view(), name='profile'),
]