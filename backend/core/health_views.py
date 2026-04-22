"""
Health check API views.
Provides read-only endpoints for system health monitoring.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status as http_status
from .health_service import HealthCheckService

<<<<<<< HEAD
logger = logging.getLogger(__name__)

=======
>>>>>>> ce7c562e (Created health dashboard and health endpoints)

class HealthStatusView(APIView):
    """
    Health status endpoint.
    Returns comprehensive health check information.
    No authentication required for operational monitoring.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get current application health status."""
        health_data = HealthCheckService.get_full_status()
        
        http_status_code = (
            http_status.HTTP_200_OK
            if health_data.get("status") == "healthy"
            else http_status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
        return Response(health_data, status=http_status_code)


class HealthReadyView(APIView):
    """
    Readiness probe endpoint.
    Returns 200 if app is ready to serve requests, 503 otherwise.
    Useful for Kubernetes/container health checks.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Check if application is ready."""
        try:
            # Quick connectivity check
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            return Response(
                {"status": "ready"},
                status=http_status.HTTP_200_OK
            )
<<<<<<< HEAD
        except Exception:
            logger.exception("Readiness check failed")
            return Response(
                {"status": "not_ready", "error": "Readiness check failed"},
=======
        except Exception as e:
            return Response(
                {"status": "not_ready", "error": str(e)},
>>>>>>> ce7c562e (Created health dashboard and health endpoints)
                status=http_status.HTTP_503_SERVICE_UNAVAILABLE
            )


class HealthLiveView(APIView):
    """
    Liveness probe endpoint.
    Returns 200 if app process is alive, 503 otherwise.
    Useful for Kubernetes/container liveness checks.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Check if application process is alive."""
        return Response(
            {"status": "alive"},
            status=http_status.HTTP_200_OK
        )
