from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/goals/', include('goals.urls')),
    path('api/v1/activities/', include('activities.urls')),
    path("api/v1/analytics/", include("analytics.urls")),
    path('api/v1/data-integrations/', include('data_integration.urls')),
]
