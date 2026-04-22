from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, ProfileUpdateView
from .presentation.views import CustomTokenObtainPairView, GoogleAuthURLView, GoogleCallbackView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # swapped
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileUpdateView.as_view(), name='profile_update'),
    path('oauth/google/', GoogleAuthURLView.as_view(), name='google_auth_url'),
    path('oauth/google/callback/', GoogleCallbackView.as_view(), name='google_callback'),
]
