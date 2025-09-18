"""
Middleware for common functionality following SOLID principles.

This module provides middleware that follows:
- Single Responsibility: Each middleware has one clear purpose
- Open/Closed: Extensible through inheritance
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
from apps.organizations.models import Organization


class OrganizationMiddleware(MiddlewareMixin):
    """
    Middleware to handle organization context in multi-tenant environment.

    Follows Single Responsibility Principle - only handles organization context.
    """

    def process_request(self, request):
        """Add organization context to request."""
        organization_slug = None

        # Try to get organization from subdomain
        host = request.get_host()
        if '.' in host:
            subdomain = host.split('.')[0]
            if subdomain not in ['www', 'api', 'admin']:
                organization_slug = subdomain

        # Try to get organization from headers (for API requests)
        if not organization_slug:
            organization_slug = request.META.get('HTTP_X_ORGANIZATION')

        # Try to get organization from URL path
        if not organization_slug and request.path.startswith('/api/org/'):
            path_parts = request.path.split('/')
            if len(path_parts) > 3:
                organization_slug = path_parts[3]

        # Set organization context
        request.organization = None
        if organization_slug:
            try:
                request.organization = Organization.objects.get(
                    slug=organization_slug,
                    is_active=True
                )
            except Organization.DoesNotExist:
                # Allow request to continue - views can handle missing organization
                pass

        return None