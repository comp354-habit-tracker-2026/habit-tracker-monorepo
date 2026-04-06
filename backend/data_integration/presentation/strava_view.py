from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from ..data.strava import StravaAuthService
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)

class StravaAuthViewSet(viewsets.ViewSet):
    """
    A stateless ViewSet for handling Strava OAuth.
    It doesn't use a Model because we aren't saving to a DB.
    """
    # 1. Allow anyone to hit this (since they aren't logged in yet)
    permission_classes = [AllowAny]
    
    # 2. REMOVE SessionAuthentication for this view. 
    # This is what triggers the CSRF 403 check.
    authentication_classes = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = StravaAuthService(
            client_id=settings.STRAVA_CLIENT_ID,
            client_secret=settings.STRAVA_CLIENT_SECRET
        )

    @action(detail=False, methods=['post'])
    def connect(self, request):
        """POST /api/strava/connect/ with {'code': '...'}"""
        code = request.data.get('code')
        if not code:
            return Response({"error": "Code is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tokens = self.auth_service.authenticateUser(code)
            return Response(tokens)
        except Exception:
            logger.exception("Error while connecting Strava account.")
            return Response(
                {"error": "An internal error occurred while connecting your Strava account."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """POST /api/v1/data-integrations/strava/refresh/ with {'refresh_token': '...'}"""
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_tokens = self.auth_service.refresh_token(refresh_token)
            return Response(new_tokens)
        except Exception:
            logger.exception("Error while refreshing Strava tokens.")
            return Response(
                {"error": "An internal error occurred while refreshing your Strava connection."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )