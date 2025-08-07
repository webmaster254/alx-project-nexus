"""
Health check utilities for production monitoring.
"""

import time
import logging
from typing import Dict, Any, List
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('performance')


class HealthCheckStatus:
    """Health check status constants."""
    HEALTHY = 'healthy'
    UNHEALTHY = 'unhealthy'
    DEGRADED = 'degraded'


class HealthChecker:
    """Health check utility class."""
    
    def __init__(self):
        self.checks = []
        self.register_default_checks()
    
    def register_default_checks(self):
        """Register default health checks."""
        if getattr(settings, 'HEALTH_CHECK_DATABASE', True):
            self.checks.append(('database', self.check_database))
        
        if getattr(settings, 'HEALTH_CHECK_CACHE', True):
            self.checks.append(('cache', self.check_cache))
        
        if getattr(settings, 'HEALTH_CHECK_STORAGE', True):
            self.checks.append(('storage', self.check_storage))
    
    def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        start_time = time.time()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            response_time = time.time() - start_time
            
            if response_time > getattr(settings, 'SLOW_QUERY_THRESHOLD', 1.0):
                return {
                    'status': HealthCheckStatus.DEGRADED,
                    'message': f'Database responding slowly ({response_time:.3f}s)',
                    'response_time': response_time,
                    'details': {
                        'connection_status': 'connected',
                        'query_result': result[0] if result else None
                    }
                }
            
            return {
                'status': HealthCheckStatus.HEALTHY,
                'message': 'Database is healthy',
                'response_time': response_time,
                'details': {
                    'connection_status': 'connected',
                    'query_result': result[0] if result else None
                }
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': HealthCheckStatus.UNHEALTHY,
                'message': f'Database connection failed: {str(e)}',
                'response_time': time.time() - start_time,
                'details': {
                    'connection_status': 'failed',
                    'error': str(e)
                }
            }
    
    def check_cache(self) -> Dict[str, Any]:
        """Check cache connectivity and performance."""
        start_time = time.time()
        test_key = 'health_check_test'
        test_value = f'test_{int(time.time())}'
        
        try:
            # Test cache write
            cache.set(test_key, test_value, timeout=60)
            
            # Test cache read
            cached_value = cache.get(test_key)
            
            # Clean up
            cache.delete(test_key)
            
            response_time = time.time() - start_time
            
            if cached_value != test_value:
                return {
                    'status': HealthCheckStatus.UNHEALTHY,
                    'message': 'Cache read/write mismatch',
                    'response_time': response_time,
                    'details': {
                        'expected': test_value,
                        'actual': cached_value
                    }
                }
            
            if response_time > 0.5:  # 500ms threshold for cache
                return {
                    'status': HealthCheckStatus.DEGRADED,
                    'message': f'Cache responding slowly ({response_time:.3f}s)',
                    'response_time': response_time,
                    'details': {
                        'operation': 'read/write successful'
                    }
                }
            
            return {
                'status': HealthCheckStatus.HEALTHY,
                'message': 'Cache is healthy',
                'response_time': response_time,
                'details': {
                    'operation': 'read/write successful'
                }
            }
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                'status': HealthCheckStatus.UNHEALTHY,
                'message': f'Cache operation failed: {str(e)}',
                'response_time': time.time() - start_time,
                'details': {
                    'error': str(e)
                }
            }
    
    def check_storage(self) -> Dict[str, Any]:
        """Check storage accessibility."""
        start_time = time.time()
        
        try:
            import os
            from django.conf import settings
            
            # Check if media directory is writable
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if media_root and os.path.exists(media_root):
                test_file = os.path.join(media_root, '.health_check')
                try:
                    with open(test_file, 'w') as f:
                        f.write('health_check')
                    os.remove(test_file)
                    writable = True
                except (IOError, OSError):
                    writable = False
            else:
                writable = False
            
            response_time = time.time() - start_time
            
            if not writable:
                return {
                    'status': HealthCheckStatus.DEGRADED,
                    'message': 'Storage is not writable',
                    'response_time': response_time,
                    'details': {
                        'media_root': str(media_root) if media_root else None,
                        'writable': writable
                    }
                }
            
            return {
                'status': HealthCheckStatus.HEALTHY,
                'message': 'Storage is healthy',
                'response_time': response_time,
                'details': {
                    'media_root': str(media_root) if media_root else None,
                    'writable': writable
                }
            }
            
        except Exception as e:
            logger.error(f"Storage health check failed: {str(e)}")
            return {
                'status': HealthCheckStatus.UNHEALTHY,
                'message': f'Storage check failed: {str(e)}',
                'response_time': time.time() - start_time,
                'details': {
                    'error': str(e)
                }
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        start_time = time.time()
        results = {}
        overall_status = HealthCheckStatus.HEALTHY
        
        for check_name, check_func in self.checks:
            try:
                result = check_func()
                results[check_name] = result
                
                # Determine overall status
                if result['status'] == HealthCheckStatus.UNHEALTHY:
                    overall_status = HealthCheckStatus.UNHEALTHY
                elif result['status'] == HealthCheckStatus.DEGRADED and overall_status == HealthCheckStatus.HEALTHY:
                    overall_status = HealthCheckStatus.DEGRADED
                    
            except Exception as e:
                logger.error(f"Health check '{check_name}' failed with exception: {str(e)}")
                results[check_name] = {
                    'status': HealthCheckStatus.UNHEALTHY,
                    'message': f'Health check failed: {str(e)}',
                    'response_time': 0,
                    'details': {'error': str(e)}
                }
                overall_status = HealthCheckStatus.UNHEALTHY
        
        total_time = time.time() - start_time
        
        return {
            'status': overall_status,
            'timestamp': time.time(),
            'total_response_time': total_time,
            'checks': results,
            'version': getattr(settings, 'VERSION', '1.0.0'),
            'environment': getattr(settings, 'ENVIRONMENT', 'production')
        }


# Global health checker instance
health_checker = HealthChecker()


@api_view(['GET'])
@permission_classes([AllowAny])
@never_cache
def health_check(request):
    """
    Comprehensive health check endpoint.
    
    Returns detailed health status of all system components.
    """
    if not getattr(settings, 'HEALTH_CHECK_ENABLED', True):
        return Response(
            {'message': 'Health checks are disabled'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    result = health_checker.run_all_checks()
    
    # Log health check results
    logger.info(f"Health check completed: {result['status']} in {result['total_response_time']:.3f}s")
    
    # Determine HTTP status code
    if result['status'] == HealthCheckStatus.HEALTHY:
        http_status = status.HTTP_200_OK
    elif result['status'] == HealthCheckStatus.DEGRADED:
        http_status = status.HTTP_200_OK  # Still operational
    else:
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(result, status=http_status)


@api_view(['GET'])
@permission_classes([AllowAny])
@never_cache
def liveness_probe(request):
    """
    Simple liveness probe for Kubernetes/Docker health checks.
    
    Returns 200 if the application is running.
    """
    return Response({
        'status': 'alive',
        'timestamp': time.time()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@never_cache
def readiness_probe(request):
    """
    Readiness probe for Kubernetes/Docker deployments.
    
    Returns 200 if the application is ready to serve traffic.
    """
    if not getattr(settings, 'HEALTH_CHECK_ENABLED', True):
        return Response({
            'status': 'ready',
            'timestamp': time.time()
        }, status=status.HTTP_200_OK)
    
    # Run critical checks only (database)
    start_time = time.time()
    
    try:
        db_result = health_checker.check_database()
        response_time = time.time() - start_time
        
        if db_result['status'] == HealthCheckStatus.UNHEALTHY:
            return Response({
                'status': 'not_ready',
                'message': 'Database not available',
                'timestamp': time.time(),
                'response_time': response_time
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({
            'status': 'ready',
            'timestamp': time.time(),
            'response_time': response_time
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Readiness probe failed: {str(e)}")
        return Response({
            'status': 'not_ready',
            'message': str(e),
            'timestamp': time.time(),
            'response_time': time.time() - start_time
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
@never_cache
def metrics(request):
    """
    Basic metrics endpoint for monitoring.
    
    Returns application metrics for monitoring systems.
    """
    import os
    try:
        import psutil
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application metrics
        process = psutil.Process(os.getpid())
        app_memory = process.memory_info()
        
        metrics_data = {
            'timestamp': time.time(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            },
            'application': {
                'memory': {
                    'rss': app_memory.rss,
                    'vms': app_memory.vms
                },
                'pid': os.getpid(),
                'threads': process.num_threads()
            },
            'database': {
                'connections': len(connection.queries) if hasattr(connection, 'queries') else 0
            }
        }
        
        return Response(metrics_data, status=status.HTTP_200_OK)
        
    except ImportError:
        # psutil not available
        return Response({
            'timestamp': time.time(),
            'message': 'Detailed metrics not available (psutil not installed)',
            'basic_metrics': {
                'pid': os.getpid(),
                'database_queries': len(connection.queries) if hasattr(connection, 'queries') else 0
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        return Response({
            'error': str(e),
            'timestamp': time.time()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)