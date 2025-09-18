"""
URL configuration for TimeTracker project.

This module provides URL routing that follows SOLID principles:
- Single Responsibility: Each URL pattern has one clear purpose
- Open/Closed: Extensible through included app URLs
- Interface Segregation: Focused URL groups for different concerns
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# API URL patterns
api_patterns = [
    # Authentication endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # App-specific API endpoints
    path('users/', include('apps.users.urls')),
    path('organizations/', include('apps.organizations.urls')),
    path('projects/', include('apps.projects.urls')),
    path('time-tracking/', include('apps.time_tracking.urls')),
    path('compliance/', include('apps.compliance.urls')),
    path('approvals/', include('apps.approvals.urls')),
    path('reports/', include('apps.reports.urls')),
]

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/v1/', include(api_patterns)),

    # Health check
    path('health/', include('apps.common.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = 'TimeTracker Pro Administration'
admin.site.site_title = 'TimeTracker Pro Admin'
admin.site.index_title = 'Welcome to TimeTracker Pro Administration'
