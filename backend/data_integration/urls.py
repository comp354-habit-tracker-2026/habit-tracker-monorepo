from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DataIntegrationViewSet

router = DefaultRouter()
router.register("", DataIntegrationViewSet, basename="data-integration")

urlpatterns = [
    path("", include(router.urls)),
]
