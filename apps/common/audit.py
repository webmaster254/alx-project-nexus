"""
Audit logging utilities for tracking sensitive operations.
"""
import logging
import json
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from functools import wraps

User = get_user_model()

# Configure audit logger
audit_logger = logging.getLogger('audit')


class AuditEvent:
    """
    Audit event types for different operations.
    """
    # Authentication events
    LOGIN_SUCCESS = 'login_success'
    LOGIN_FAILED = 'login_failed'
    LOGOUT = 'logout'
    PASSWORD_CHANGE = 'password_change'
    ACCOUNT_CREATED = 'account_created'
    ACCOUNT_DEACTIVATED = 'account_deactivated'
    
    # Job management events
    JOB_CREATED = 'job_created'
    JOB_UPDATED = 'job_updated'
    JOB_DELETED = 'job_deleted'
    JOB_ACTIVATED = 'job_activated'
    JOB_DEACTIVATED = 'job_deactivated'
    
    # Application events
    APPLICATION_SUBMITTED = 'application_submitted'
    APPLICATION_STATUS_CHANGED = 'application_status_changed'
    APPLICATION_WITHDRAWN = 'application_withdrawn'
    
    # Admin events
    USER_ROLE_CHANGED = 'user_role_changed'
    BULK_OPERATION = 'bulk_operation'
    DATA_EXPORT = 'data_export'
    
    # Security events
    UNAUTHORIZED_ACCESS = 'unauthorized_access'
    RATE_LIMIT_EXCEEDED = 'rate_limit_exceeded'
    SUSPICIOUS_ACTIVITY = 'suspicious_activity'


def log_audit_event(event_type, user=None, resource_type=None, resource_id=None, 
                   details=None, ip_address=None, user_agent=None, success=True):
    """
    Log an audit event with structured data.
    
    Args:
        event_type (str): Type of event from AuditEvent class
        user (User): User who performed the action
        resource_type (str): Type of resource affected (e.g., 'job', 'application')
        resource_id (str/int): ID of the affected resource
        details (dict): Additional details about the event
        ip_address (str): IP address of the user
        user_agent (str): User agent string
        success (bool): Whether the operation was successful
    """
    audit_data = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'event_type': event_type,
        'success': success,
        'user_id': user.id if user and user.is_authenticated else None,
        'username': user.username if user and user.is_authenticated else 'anonymous',
        'user_email': user.email if user and user.is_authenticated else None,
        'resource_type': resource_type,
        'resource_id': str(resource_id) if resource_id else None,
        'ip_address': ip_address,
        'user_agent': user_agent,
        'details': details or {}
    }
    
    # Log as JSON for structured logging
    audit_logger.info(json.dumps(audit_data))


def audit_log(event_type, resource_type=None, include_request_data=False):
    """
    Decorator for automatically logging audit events for view functions.
    
    Args:
        event_type (str): Type of event from AuditEvent class
        resource_type (str): Type of resource being affected
        include_request_data (bool): Whether to include request data in details
    
    Returns:
        function: Decorated view function
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Get request metadata
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Prepare details
            details = {
                'method': request.method,
                'path': request.path,
                'view_name': view_func.__name__
            }
            
            if include_request_data and hasattr(request, 'data'):
                # Sanitize sensitive data
                sanitized_data = sanitize_request_data(request.data)
                details['request_data'] = sanitized_data
            
            try:
                # Execute the view
                response = view_func(request, *args, **kwargs)
                
                # Determine resource ID from response or kwargs
                resource_id = None
                if 'pk' in kwargs:
                    resource_id = kwargs['pk']
                elif 'id' in kwargs:
                    resource_id = kwargs['id']
                elif hasattr(response, 'data') and isinstance(response.data, dict):
                    resource_id = response.data.get('id')
                
                # Log successful operation
                log_audit_event(
                    event_type=event_type,
                    user=request.user,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True
                )
                
                return response
                
            except Exception as e:
                # Log failed operation
                details['error'] = str(e)
                log_audit_event(
                    event_type=event_type,
                    user=request.user,
                    resource_type=resource_type,
                    details=details,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False
                )
                raise
        
        return wrapped_view
    return decorator


def get_client_ip(request):
    """
    Get the client IP address from the request.
    
    Args:
        request: Django request object
    
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def sanitize_request_data(data):
    """
    Sanitize request data to remove sensitive information.
    
    Args:
        data (dict): Request data
    
    Returns:
        dict: Sanitized data
    """
    if not isinstance(data, dict):
        return data
    
    sensitive_fields = [
        'password', 'confirm_password', 'old_password', 'new_password',
        'token', 'refresh', 'access', 'secret', 'key', 'api_key'
    ]
    
    sanitized = {}
    for key, value in data.items():
        if key.lower() in sensitive_fields:
            sanitized[key] = '[REDACTED]'
        elif isinstance(value, dict):
            sanitized[key] = sanitize_request_data(value)
        else:
            sanitized[key] = value
    
    return sanitized


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware for automatic audit logging of sensitive operations.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Process incoming request for audit logging.
        """
        # Store request start time for performance tracking
        request._audit_start_time = datetime.utcnow()
        return None
    
    def process_response(self, request, response):
        """
        Process response for audit logging.
        """
        # Log authentication events
        if request.path.startswith('/api/auth/'):
            self._log_auth_event(request, response)
        
        # Log admin operations
        if request.path.startswith('/admin/'):
            self._log_admin_event(request, response)
        
        return response
    
    def process_exception(self, request, exception):
        """
        Process exceptions for audit logging.
        """
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        details = {
            'method': request.method,
            'path': request.path,
            'exception_type': exception.__class__.__name__,
            'exception_message': str(exception)
        }
        
        log_audit_event(
            event_type=AuditEvent.SUSPICIOUS_ACTIVITY,
            user=request.user if hasattr(request, 'user') else None,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False
        )
        
        return None
    
    def _log_auth_event(self, request, response):
        """
        Log authentication-related events.
        """
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        path = request.path
        method = request.method
        status_code = response.status_code
        
        details = {
            'method': method,
            'path': path,
            'status_code': status_code
        }
        
        # Determine event type based on path and status
        if '/login/' in path and method == 'POST':
            event_type = AuditEvent.LOGIN_SUCCESS if status_code == 200 else AuditEvent.LOGIN_FAILED
        elif '/logout/' in path and method == 'POST':
            event_type = AuditEvent.LOGOUT
        elif '/register/' in path and method == 'POST':
            event_type = AuditEvent.ACCOUNT_CREATED if status_code == 201 else None
        elif '/change-password/' in path and method == 'POST':
            event_type = AuditEvent.PASSWORD_CHANGE if status_code == 200 else None
        else:
            return  # Don't log other auth endpoints
        
        if event_type:
            log_audit_event(
                event_type=event_type,
                user=request.user if hasattr(request, 'user') else None,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent,
                success=status_code < 400
            )
    
    def _log_admin_event(self, request, response):
        """
        Log admin panel events.
        """
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return
        
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        details = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code
        }
        
        log_audit_event(
            event_type=AuditEvent.BULK_OPERATION,
            user=request.user,
            resource_type='admin',
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=response.status_code < 400
        )


# Convenience functions for common audit events
def log_login_success(user, request):
    """Log successful login."""
    log_audit_event(
        event_type=AuditEvent.LOGIN_SUCCESS,
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


def log_login_failed(username, request):
    """Log failed login attempt."""
    log_audit_event(
        event_type=AuditEvent.LOGIN_FAILED,
        details={'attempted_username': username},
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


def log_job_created(user, job, request):
    """Log job creation."""
    log_audit_event(
        event_type=AuditEvent.JOB_CREATED,
        user=user,
        resource_type='job',
        resource_id=job.id,
        details={'job_title': job.title, 'company': job.company.name},
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


def log_application_submitted(user, application, request):
    """Log job application submission."""
    log_audit_event(
        event_type=AuditEvent.APPLICATION_SUBMITTED,
        user=user,
        resource_type='application',
        resource_id=application.id,
        details={
            'job_id': application.job.id,
            'job_title': application.job.title,
            'company': application.job.company.name
        },
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )


def log_unauthorized_access(request, resource_type=None, resource_id=None):
    """Log unauthorized access attempt."""
    log_audit_event(
        event_type=AuditEvent.UNAUTHORIZED_ACCESS,
        user=request.user if hasattr(request, 'user') else None,
        resource_type=resource_type,
        resource_id=resource_id,
        details={
            'method': request.method,
            'path': request.path,
            'attempted_resource': f"{resource_type}:{resource_id}" if resource_type and resource_id else None
        },
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        success=False
    )