from django.urls import path, include
from rest_framework.routers import DefaultRouter

from gamification.presentation.viewsets import (
    BadgeViewSet,
    MilestoneViewSet,
    StreakViewSet,
    SummaryViewSet,
    EvaluateViewSet,
)

router = DefaultRouter()
router.register('badges', BadgeViewSet, basename='badge')
router.register('milestones', MilestoneViewSet, basename='milestone')
router.register('streaks', StreakViewSet, basename='streak')
router.register('summary', SummaryViewSet, basename='summary')
router.register('evaluate', EvaluateViewSet, basename='evaluate')

urlpatterns = [
    path('', include(router.urls)),
]
