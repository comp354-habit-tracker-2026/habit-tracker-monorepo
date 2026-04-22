from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from mywhoosh_integration.serializers import SyncStatusSerializer
from mywhoosh_integration.services.sync_status_service import SyncStatusService
from mywhoosh_integration.mywhoosh_mapper import map_mywhoosh_session
from mywhoosh_integration.session_persistence_service import SessionPersistenceService
from mywhoosh_integration.sync_status_services import SyncStatusService

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

class MyWhooshSyncView(APIView):
    """
    Triggers a MyWhoosh synchronization for a given user.

    Temporary assumption for Milestone #3:
    - user_id is provided in the request body until full auth is integrated.
    - raw sessions are mocked until real provider fetching is added.
    """

    def post(self, request):
        user_id = request.data.get("user_id")

        if user_id is None:
            return Response(
                {"detail": "Missing required field: user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "user_id must be an integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_sessions = [
            {
                "session_id": "mw_001",
                "activity_type": "cycling",
                "date": "2026-04-05",
                "distance": 24.5,
                "calories": 420,
                "duration": 3600,
            },
            {
                "session_id": "mw_002",
                "activity_type": "cycling",
                "date": "2026-04-06",
                "distance": 18.0,
                "calories": 310,
                "duration": 2800,
            },
        ]

        try:
            normalized_sessions = [
                map_mywhoosh_session(raw_session)
                for raw_session in raw_sessions
            ]

            result = SessionPersistenceService.import_sessions(
                user_id=user_id,
                sessions=normalized_sessions,
            )

            sessions_imported = result["sessions_imported"]
            duplicates_skipped = result["duplicates_skipped"]

            if sessions_imported > 0 and duplicates_skipped > 0:
                sync_status = SyncStatusService.record_partial(
                    user_id=user_id,
                    sessions_imported=sessions_imported,
                    duplicates_skipped=duplicates_skipped,
                    error_message="Some sessions were skipped as duplicates.",
                )
            else:
                sync_status = SyncStatusService.record_success(
                    user_id=user_id,
                    sessions_imported=sessions_imported,
                    duplicates_skipped=duplicates_skipped,
                )

            serializer = SyncStatusSerializer(sync_status)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            sync_status = SyncStatusService.record_failure(
                user_id=user_id,
                error_message=str(exc),
            )
            serializer = SyncStatusSerializer(sync_status)
            return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
