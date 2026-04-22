from django.urls import path

from data_integration.presentation.privacy_views import (
    PrivacyHistoryView,
    PrivacyUpdateView,
    PrivacyVerifyView,
)


urlpatterns = [
    path('verify', PrivacyVerifyView.as_view(), name='privacy-verify'),
    path('update', PrivacyUpdateView.as_view(), name='privacy-update'),
    path('history', PrivacyHistoryView.as_view(), name='privacy-history'),
]
