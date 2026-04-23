from django.urls import include, path
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from data_integration.presentation.mapmyrun_views import get_mapmyrun_activities
from .views import FileRecordViewSet, StravaAuthViewSet, WeskiUploadViewSet, upload_mapmyrun_file


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def integration_root(request):
    return JsonResponse({"message": "This is the data-integration route"})


router = DefaultRouter()
router.register(r'files', FileRecordViewSet, basename="file-record")
router.register(r'strava', StravaAuthViewSet, basename="strava")
router.register(r'weski', WeskiUploadViewSet, basename="weski")


urlpatterns = [
    path('', integration_root, name='integration-root'),
    path('', include(router.urls)),
    path('upload/mapmyrun/<int:user_id>/', upload_mapmyrun_file, name='upload-mapmyrun-file'),
    path("activities/mapmyrun/<int:user_id>/", get_mapmyrun_activities, name='get-mapmyrun-activities'),
]
