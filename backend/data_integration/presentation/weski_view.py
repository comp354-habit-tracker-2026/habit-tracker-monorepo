import logging

from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from activities.models import Activity, ConnectedAccount
from data_integration.data.weski import WeskiGpxService

logger = logging.getLogger(__name__)


class WeskiUploadViewSet(viewsets.ViewSet):
    """ViewSet for uploading weSki GPX files and creating Activity records."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gpx_service = WeskiGpxService()

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        """POST /api/v1/data-integrations/weski/upload/ with a GPX file."""
        gpx_file = request.FILES.get("file")
        if not gpx_file:
            return Response(
                {"error": "A GPX file is required. Upload it as the 'file' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not gpx_file.name.lower().endswith(".gpx"):
            return Response(
                {"error": "Only .gpx files are accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            gpx_content = gpx_file.read()
            summary = self.gpx_service.parse_gpx(gpx_content)
        except Exception:
            logger.exception("Failed to parse weSki GPX file.")
            return Response(
                {"error": "Failed to parse the GPX file. Please ensure it is a valid weSki GPX export."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create a weski ConnectedAccount for this user
        account, _ = ConnectedAccount.objects.get_or_create(
            user=request.user,
            provider="weski",
            defaults={"external_user_id": f"weski_{request.user.pk}"},
        )

        # Check for duplicate
        if Activity.objects.filter(account=account, external_id=summary.external_id).exists():
            return Response(
                {"error": "This GPX session has already been uploaded."},
                status=status.HTTP_409_CONFLICT,
            )

        # Create the Activity record
        duration_minutes = int(summary.total_time_seconds / 60) if summary.total_time_seconds else 0
        activity = Activity.objects.create(
            account=account,
            activity_type="skiing",
            duration=duration_minutes,
            date=summary.start_time.date() if summary.start_time else None,
            external_id=summary.external_id,
            distance=round(summary.total_distance_km, 2),
            raw_data={
                "track_name": summary.track_name,
                "total_elevation_gain_meters": summary.total_elevation_gain_meters,
                "number_of_runs": summary.number_of_runs,
                "total_time_seconds": summary.total_time_seconds,
                "average_speed_kmh": summary.average_speed_kmh,
                "max_speed_kmh": summary.max_speed_kmh,
            },
        )

        return Response(
            {
                "id": activity.id,
                "activity_type": activity.activity_type,
                "date": str(activity.date),
                "duration_minutes": activity.duration,
                "distance_km": float(activity.distance),
                "provider": account.provider,
                "external_id": activity.external_id,
                "track_name": summary.track_name,
                "number_of_runs": summary.number_of_runs,
                "total_elevation_gain_meters": summary.total_elevation_gain_meters,
                "average_speed_kmh": summary.average_speed_kmh,
                "max_speed_kmh": summary.max_speed_kmh,
            },
            status=status.HTTP_201_CREATED,
        )
