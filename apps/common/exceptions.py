"""
Custom exception handlers and error response utilities.
"""
import logging
from datetime import datetime
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    NotAcceptable,
    UnsupportedMediaType,
    Throttled,
    ParseError,
)

logger = logging.getLogger(__name__)


class CustomAPIException(Exception):
    """
    Base custom API exception class.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        
        self.detail = detail
        self.code = code


class BusinessLogicError(CustomAPIException):
    """
    Exception for business logic violations.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Business logic error occurred.'
    default_code = 'business_logic_error'


class DuplicateApplicationError(BusinessLogicError):
    """
    Exception for duplicate job applications.
    """
    default_detail = 'You have already applied for this job.'
    default_code = 'duplicate_application'


class InactiveJobError(BusinessLogicError):
    """
    Exception for operations on inactive jobs.
    """
    default_detail = 'This job is no longer active.'
    default_code = 'inactive_job'


class InvalidFileTypeError(ValidationError):
    """
    Exception for invalid file uploads.
    """
    default_detail = 'Invalid file type.'
    default_code = 'invalid_file_type'


def format_error_response(error_code, message, details=None, status_code=400):
    """
    Format a consistent error response structure.
    
    Args:
        error_code (str): Error code identifier
        message (str): Human-readable error message
        details (dict): Additional error details
        status_code (int): HTTP status code
    
    Returns:
        dict: Formatted error response
    """
    error_response = {
        'error': {
            'code': error_code,
            'message': message,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    }
    
    if details:
        error_response['error']['details'] = details
    
    return error_response


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    
    Args:
        exc: The exception instance
        context: The context in which the exception occurred
    
    Returns:
        Response: Formatted error response
    """
    # Get the standard error response first
    response = exception_handler(exc, context)
    
    # Log the exception for debugging
    request = context.get('request')
    if request:
        logger.error(
            f"API Exception: {exc.__class__.__name__} - {str(exc)} "
            f"- Path: {request.path} - Method: {request.method} "
            f"- User: {getattr(request.user, 'email', 'Anonymous')}"
        )
    
    # Handle custom exceptions
    if isinstance(exc, CustomAPIException):
        error_data = format_error_response(
            error_code=exc.code,
            message=str(exc.detail),
            status_code=exc.status_code
        )
        return Response(error_data, status=exc.status_code)
    
    # Handle standard DRF exceptions
    if response is not None:
        custom_response_data = None
        
        if isinstance(exc, ValidationError):
            # Handle validation errors
            details = {}
            if isinstance(response.data, dict):
                for field, errors in response.data.items():
                    if isinstance(errors, list):
                        details[field] = [str(error) for error in errors]
                    else:
                        details[field] = [str(errors)]
            elif isinstance(response.data, list):
                details['non_field_errors'] = [str(error) for error in response.data]
            else:
                details['non_field_errors'] = [str(response.data)]
            
            custom_response_data = format_error_response(
                error_code='VALIDATION_ERROR',
                message='Invalid input data provided.',
                details=details,
                status_code=response.status_code
            )
        
        elif isinstance(exc, AuthenticationFailed):
            custom_response_data = format_error_response(
                error_code='AUTHENTICATION_FAILED',
                message='Authentication credentials were not provided or are invalid.',
                status_code=response.status_code
            )
        
        elif isinstance(exc, PermissionDenied):
            custom_response_data = format_error_response(
                error_code='PERMISSION_DENIED',
                message='You do not have permission to perform this action.',
                status_code=response.status_code
            )
        
        elif isinstance(exc, NotFound):
            custom_response_data = format_error_response(
                error_code='NOT_FOUND',
                message='The requested resource was not found.',
                status_code=response.status_code
            )
        
        elif isinstance(exc, MethodNotAllowed):
            allowed_methods = getattr(exc, 'detail', {}).get('allowed_methods', [])
            custom_response_data = format_error_response(
                error_code='METHOD_NOT_ALLOWED',
                message=f'Method not allowed. Allowed methods: {", ".join(allowed_methods)}',
                status_code=response.status_code
            )
        
        elif isinstance(exc, Throttled):
            custom_response_data = format_error_response(
                error_code='RATE_LIMIT_EXCEEDED',
                message=f'Rate limit exceeded. Try again in {exc.wait} seconds.',
                details={'retry_after': exc.wait},
                status_code=response.status_code
            )
        
        elif isinstance(exc, ParseError):
            custom_response_data = format_error_response(
                error_code='PARSE_ERROR',
                message='Malformed request data.',
                status_code=response.status_code
            )
        
        elif isinstance(exc, (NotAcceptable, UnsupportedMediaType)):
            custom_response_data = format_error_response(
                error_code='MEDIA_TYPE_ERROR',
                message='Unsupported media type or format.',
                status_code=response.status_code
            )
        
        if custom_response_data:
            response.data = custom_response_data
    
    # Handle Django exceptions that don't have DRF responses
    elif isinstance(exc, Http404):
        error_data = format_error_response(
            error_code='NOT_FOUND',
            message='The requested resource was not found.',
            status_code=404
        )
        response = Response(error_data, status=status.HTTP_404_NOT_FOUND)
    
    elif isinstance(exc, DjangoValidationError):
        details = {}
        if hasattr(exc, 'message_dict'):
            for field, errors in exc.message_dict.items():
                details[field] = errors
        else:
            details['non_field_errors'] = exc.messages if hasattr(exc, 'messages') else [str(exc)]
        
        error_data = format_error_response(
            error_code='VALIDATION_ERROR',
            message='Invalid data provided.',
            details=details,
            status_code=400
        )
        response = Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    elif isinstance(exc, IntegrityError):
        error_data = format_error_response(
            error_code='INTEGRITY_ERROR',
            message='Database integrity constraint violation.',
            status_code=400
        )
        response = Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle unexpected server errors
    elif response is None:
        logger.error(f"Unhandled exception: {exc.__class__.__name__} - {str(exc)}")
        error_data = format_error_response(
            error_code='INTERNAL_SERVER_ERROR',
            message='An unexpected error occurred. Please try again later.',
            status_code=500
        )
        response = Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


def handle_404(request, exception=None):
    """
    Custom 404 handler for API endpoints.
    """
    error_data = format_error_response(
        error_code='NOT_FOUND',
        message='The requested endpoint was not found.',
        status_code=404
    )
    return Response(error_data, status=status.HTTP_404_NOT_FOUND)


def handle_500(request):
    """
    Custom 500 handler for API endpoints.
    """
    logger.error(f"Server error on path: {request.path}")
    error_data = format_error_response(
        error_code='INTERNAL_SERVER_ERROR',
        message='An internal server error occurred. Please try again later.',
        status_code=500
    )
    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)