from django.urls import path
from .views import update_user_profile

urlpatterns = [
    path('users/<int:user_id>/update/', update_user_profile, name='update_user'),
]