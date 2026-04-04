from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mywhoosh_integration.serializers import SyncStatusSerializer
from mywhoosh_integration.services.sync_status_service import SyncStatusService

def health(request):
    return JsonResponse({"status": "ok"})

## For the syncronization status
class MyWhooshSyncStatusView(APIView):
    """
    Returns the latest sync status for a given user.

    Temporary assumption for Milestone #2:
    - user_id is provided through query parameters until the full auth flow
      is integrated.
    """

    def get(self, request):
        user_id_param = request.query_params.get("user_id")

        if user_id_param is None:
            return Response(
                {"detail": "Missing required query parameter: user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = int(user_id_param)
        except ValueError:
            return Response(
                {"detail": "user_id must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        latest_status = SyncStatusService.get_latest_for_user(user_id)

        if latest_status is None:
            return Response(
                {"detail": "No sync status found for this user"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SyncStatusSerializer(latest_status)
        return Response(serializer.data, status=status.HTTP_200_OK)
