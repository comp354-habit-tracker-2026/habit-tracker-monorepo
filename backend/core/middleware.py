import time
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class JWTAuthenticationMiddleware:
    """
    Middleware that validates Bearer token format before
    SimpleJWT processes the request.
    Handles:
      - Malformed Authorization header → 400
      - Missing Bearer scheme → 400
    Token validation (signature, expiry) is handled by SimpleJWT.
    """

    EXEMPT_PATHS = [
        '/api/v1/auth/login/',
        '/api/v1/auth/register/',
        '/api/v1/auth/refresh/',
        '/admin/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Skip validation for exempt paths
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return self.get_response(request)

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if auth_header:
            # Validate format: must be "Bearer <token>"
            parts = auth_header.split()

            if len(parts) == 1:
                return JsonResponse(
                    {'error': 'Malformed Authorization header. Token missing after Bearer.'},
                    status=400
                )

            if parts[0].lower() != 'bearer':
                return JsonResponse(
                    {'error': 'Invalid authentication scheme. Use Bearer token.'},
                    status=400
                )

            if len(parts) > 2:
                return JsonResponse(
                    {'error': 'Malformed Authorization header. Too many parts.'},
                    status=400
                )

        response = self.get_response(request)

        # Log performance
        duration_ms = (time.time() - start_time) * 1000
        logger.debug(f"Auth middleware processed in {duration_ms:.2f}ms")

        return response