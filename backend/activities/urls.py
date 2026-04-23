from django.urls import path, include
from rest_framework.routers import DefaultRouter
from activities.presentation import ActivityViewSet, ConnectedAccountViewSet

router = DefaultRouter()
router.register('', ActivityViewSet, basename='activity')
router.register('connected-accounts', ConnectedAccountViewSet, basename='connected-account')

urlpatterns = [
    path('', include(router.urls)),
]
