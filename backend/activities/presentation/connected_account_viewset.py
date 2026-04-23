from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import ConnectedAccount
from activities.serializers import ConnectedAccountSerializer
from core.presentation.permissions import IsAdminOrOwner
import logging

logger = logging.getLogger(__name__)

class ConnectedAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user's connected third-party accounts (Strava, weSki, etc.).
    
    Provides endpoints to:
    - List user's connected accounts
    - Disconnect (remove) a connected account
    """
    
    serializer_class = ConnectedAccountSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        """Only return accounts belonging to the authenticated user"""
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return ConnectedAccount.objects.all()
        return ConnectedAccount.objects.filter(user=user)

    def perform_create(self, serializer):
        """Associate the account with the authenticated user"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """
        Disconnect a linked account by removing access tokens.
        
        POST /api/v1/connected-accounts/{id}/disconnect/
        
        This action:
        1. Clears the access_token and refresh_token
        2. Optionally deletes associated activities (based on query param)
        3. Prevents future data syncing with the provider
        """
        account = self.get_object()
        
        # Verify the user owns this account
        if account.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You do not have permission to disconnect this account."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Get query parameter to determine if activities should be deleted
        delete_activities = request.data.get('delete_activities', False)
        provider = account.provider
        
        try:
            # Delete associated activities if requested
            if delete_activities:
                account.activities.all().delete()
            
            # Clear tokens to prevent further syncing
            account.access_token = None
            account.refresh_token = None
            account.token_expires_at = None
            account.save()
            
            return Response(
                {
                    "success": True,
                    "message": f"Successfully disconnected {provider} account.",
                    "provider": provider,
                    "activities_deleted": delete_activities,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.exception("Failed to disconnect %s account.", provider)
            return Response(
                {
                    "error": "An internal error occurred while disconnecting the account.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
