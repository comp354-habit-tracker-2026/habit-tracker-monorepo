"""
Health status service for system integration monitoring.
Collects real-time health information about the application.
"""

import logging

from django.db import connection
from django.apps import apps
from django.contrib.auth import get_user_model
from typing import Dict, List, Any
from datetime import datetime

User = get_user_model()
logger = logging.getLogger(__name__)


class HealthCheckService:
    """Service to check and report application health status."""
    
    @staticmethod
    def check_database() -> Dict[str, Any]:
        """Check database connectivity and responsiveness."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return {
                "status": "healthy",
                "message": "Database is responding",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def check_migrations() -> Dict[str, Any]:
        """Check if all migrations have been applied."""
        try:
            from django.core.management import call_command
            from io import StringIO
            out = StringIO()
            call_command('migrate', '--check', stdout=out, verbosity=0)
            return {
                "status": "healthy",
                "message": "All migrations applied",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Migration check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def check_user_model() -> Dict[str, Any]:
        """Check if User model is accessible and queryable."""
        try:
            user_count = User.objects.count()
            return {
                "status": "healthy",
                "message": f"User model accessible ({user_count} users)",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"User model error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def check_installed_apps() -> Dict[str, Any]:
        """Check if all required apps are installed."""
        required_apps = [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'rest_framework',
            'users',
            'activities',
            'goals',
            'analytics',
        ]
        from django.conf import settings
        installed = settings.INSTALLED_APPS
        missing = [app for app in required_apps if app not in installed]
        
        if not missing:
            return {
                "status": "healthy",
                "message": f"All required apps installed ({len(required_apps)} apps)",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "message": f"Missing apps: {', '.join(missing)}",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def check_rest_framework() -> Dict[str, Any]:
        """Check if Django REST Framework is installed."""
        try:
            import rest_framework
            return {
                "status": "healthy",
                "message": "Django REST Framework installed",
                "timestamp": datetime.utcnow().isoformat()
            }
        except ImportError:
            return {
                "status": "unhealthy",
                "message": "Django REST Framework not installed",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def check_jwt_auth() -> Dict[str, Any]:
        """Check if JWT authentication is installed."""
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            return {
                "status": "healthy",
                "message": "JWT authentication installed",
                "timestamp": datetime.utcnow().isoformat()
            }
        except ImportError:
            return {
                "status": "unhealthy",
                "message": "JWT authentication not installed",
                "timestamp": datetime.utcnow().isoformat()
            }

    @staticmethod
    def get_full_status() -> Dict[str, Any]:
        """Get complete health status of the application."""
        checks = {
            "database": HealthCheckService.check_database(),
            "migrations": HealthCheckService.check_migrations(),
            "user_model": HealthCheckService.check_user_model(),
            "installed_apps": HealthCheckService.check_installed_apps(),
            "rest_framework": HealthCheckService.check_rest_framework(),
            "jwt_auth": HealthCheckService.check_jwt_auth(),
        }
        
        # Calculate overall status
        unhealthy_checks = [
            check for check in checks.values() 
            if check.get("status") == "unhealthy"
        ]
        
        overall_status = "unhealthy" if unhealthy_checks else "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
            "summary": {
                "total": len(checks),
                "healthy": len(checks) - len(unhealthy_checks),
                "unhealthy": len(unhealthy_checks),
            }
        }
