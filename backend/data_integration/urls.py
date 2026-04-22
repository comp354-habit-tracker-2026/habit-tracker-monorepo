from django.urls import include, path
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import DataIntegrationViewSet, StravaAuthViewSet, WeskiUploadViewSet
from .views import FileRecordViewSet, StravaAuthViewSet, WeskiUploadViewSet
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes

# 1. Create a simple view for the root of the integration path
# Use this to test that you can connect to this subsystem in the first place
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def integration_root(request):
    return JsonResponse({"message": "This is the data-integration route"})

# 2. Setup the Router
# We register 'strava' as the prefix. 
# The @action decorators in your ViewSet (connect/refresh) 
# will automatically become /strava/connect/ and /strava/refresh/
router = DefaultRouter()
router.register(r'', DataIntegrationViewSet, basename='data-integrations')
router.register(r'files', FileRecordViewSet, basename="file-record")
router.register(r'strava', StravaAuthViewSet, basename="strava")
router.register(r'weski', WeskiUploadViewSet, basename="weski")

urlpatterns = [
    # Health endpoint for this subsystem.
    path('health/', integration_root, name='integration-root'),
        
        # This includes all the routes the router generated
        # Result: /data-integration/strava/connect/
        path('', include(router.urls)),
]