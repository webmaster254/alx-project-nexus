from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import traceback
import sys
import os
from django.conf import settings

# Create your views here.

@csrf_exempt
@require_http_methods(["GET", "POST"])
def debug_info(request):
    """
    Debug endpoint to help troubleshoot deployment issues.
    Remove this endpoint after debugging is complete.
    """
    try:
        debug_data = {
            "method": request.method,
            "path": request.path,
            "host": request.get_host(),
            "allowed_hosts": getattr(settings, 'ALLOWED_HOSTS', []),
            "debug_mode": getattr(settings, 'DEBUG', False),
            "database_config": {
                "engine": settings.DATABASES['default']['ENGINE'] if settings.DATABASES else None,
                "name": settings.DATABASES['default'].get('NAME', 'Not set') if settings.DATABASES else None,
            },
            "python_version": sys.version,
            "django_version": getattr(settings, 'DJANGO_VERSION', 'Unknown'),
            "environment_vars": {
                "SECRET_KEY_SET": bool(os.environ.get('SECRET_KEY')),
                "DATABASE_URL_SET": bool(os.environ.get('DATABASE_URL')),
                "ALLOWED_HOSTS_ENV": os.environ.get('ALLOWED_HOSTS', 'Not set'),
            }
        }
        
        return JsonResponse({
            "status": "success",
            "debug_info": debug_data
        })
    except Exception as e:
        return JsonResponse({
            "status": "error", 
            "error": str(e),
            "traceback": traceback.format_exc()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def test_auth_register(request):
    """
    Debug wrapper around the auth register endpoint to capture errors.
    Remove this endpoint after debugging is complete.
    """
    try:
        # Import here to avoid circular imports
        from apps.authentication.views import register_view
        
        # Call the actual register view
        return register_view(request)
        
    except Exception as e:
        return JsonResponse({
            "status": "debug_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "request_data": {
                "method": request.method,
                "path": request.path,
                "content_type": request.content_type,
                "has_body": bool(request.body),
            }
        }, status=500)
