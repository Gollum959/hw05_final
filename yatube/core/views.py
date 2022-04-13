from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Custom page for 404 page_not_found."""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def permission_denied(
    request: HttpRequest,
    exception: Exception = None
) -> HttpResponse:
    """Custom page for 403 permission_denied."""
    return render(request, 'core/403.html', status=403)


def server_error(
    request: HttpRequest,
    exception: Exception = None
) -> HttpResponse:
    """Custom page for 500 server_error."""
    return render(request, 'core/500.html', status=500)


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    """Custom page for 403 permission_denied_view"""
    return render(request, 'core/403csrf.html')
