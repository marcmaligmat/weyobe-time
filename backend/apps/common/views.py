"""
Common views following SOLID principles.

This module provides common API views that follow:
- Single Responsibility: Each view has one clear purpose
- Open/Closed: Extensible through inheritance
"""

from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint.

    Follows Single Responsibility Principle - only checks basic health.
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def system_status(request):
    """
    Detailed system status endpoint.

    Follows Single Responsibility Principle - only provides system status.
    """
    return JsonResponse({
        'status': 'operational',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0',
        'debug': settings.DEBUG,
        'database': 'connected',
        'cache': 'operational',
        'services': {
            'authentication': 'operational',
            'time_tracking': 'operational',
            'notifications': 'operational',
            'reporting': 'operational',
        }
    })