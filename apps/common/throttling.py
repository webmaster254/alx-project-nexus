"""
Custom throttling classes and rate limiting utilities.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
from django.http import JsonResponse
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class LoginRateThrottle(UserRateThrottle):
    """
    Rate throttle for login attempts.
    """
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """
    Rate throttle for registration attempts.
    """
    scope = 'register'


class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Rate throttle for password reset attempts.
    """
    scope = 'password_reset'
    rate = '3/hour'


class APICallRateThrottle(UserRateThrottle):
    """
    General API call rate throttle for authenticated users.
    """
    scope = 'api_calls'
    rate = '1000/hour'


class SearchRateThrottle(UserRateThrottle):
    """
    Rate throttle for search operations.
    """
    scope = 'search'
    rate = '100/hour'


def api_ratelimit(group=None, key=None, rate='100/h', method='ALL', block=True):
    """
    Decorator for API rate limiting using django-ratelimit.
    
    Args:
        group (str): Rate limit group name
        key (str): Key function for rate limiting
        rate (str): Rate limit (e.g., '100/h', '10/m')
        method (str): HTTP methods to limit
        block (bool): Whether to block or just track
    
    Returns:
        function: Decorated view function
    """
    def decorator(view_func):
        @wraps(view_func)
        @ratelimit(group=group, key=key, rate=rate, method=method, block=block)
        def wrapped_view(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except Ratelimited:
                logger.warning(
                    f"Rate limit exceeded for {request.user if request.user.is_authenticated else 'anonymous'} "
                    f"on {request.path}"
                )
                return JsonResponse({
                    'error': {
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'message': 'Rate limit exceeded. Please try again later.',
                        'timestamp': '2024-01-01T00:00:00Z'
                    }
                }, status=429)
        return wrapped_view
    return decorator


def user_ratelimit(rate='100/h', method='ALL', block=True):
    """
    Rate limit decorator based on user ID.
    """
    return api_ratelimit(
        group='user',
        key='user',
        rate=rate,
        method=method,
        block=block
    )


def ip_ratelimit(rate='100/h', method='ALL', block=True):
    """
    Rate limit decorator based on IP address.
    """
    return api_ratelimit(
        group='ip',
        key='ip',
        rate=rate,
        method=method,
        block=block
    )


def login_ratelimit(rate='5/m', method='POST', block=True):
    """
    Rate limit decorator for login attempts.
    """
    return api_ratelimit(
        group='login',
        key='ip',
        rate=rate,
        method=method,
        block=block
    )


def register_ratelimit(rate='3/m', method='POST', block=True):
    """
    Rate limit decorator for registration attempts.
    """
    return api_ratelimit(
        group='register',
        key='ip',
        rate=rate,
        method=method,
        block=block
    )


def search_ratelimit(rate='50/m', method='GET', block=True):
    """
    Rate limit decorator for search operations.
    """
    return api_ratelimit(
        group='search',
        key='user_or_ip',
        rate=rate,
        method=method,
        block=block
    )


class RateLimitMiddleware:
    """
    Middleware to handle rate limiting exceptions globally.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            logger.warning(
                f"Rate limit exceeded for {request.user if request.user.is_authenticated else 'anonymous'} "
                f"on {request.path}"
            )
            return JsonResponse({
                'error': {
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'message': 'Rate limit exceeded. Please try again later.',
                    'timestamp': '2024-01-01T00:00:00Z'
                }
            }, status=429)
        return None