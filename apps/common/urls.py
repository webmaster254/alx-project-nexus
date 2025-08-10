"""
URL configuration for common app.
"""

from django.urls import path
from . import health, views

app_name = 'common'

urlpatterns = [
    # Health check endpoints
    path('health/', health.health_check, name='health_check'),
    path('health/live/', health.liveness_probe, name='liveness_probe'),
    path('health/ready/', health.readiness_probe, name='readiness_probe'),
    path('metrics/', health.metrics, name='metrics'),
    
    # Debug endpoints (remove after debugging)
    path('debug/', views.debug_info, name='debug_info'),
    path('test-register/', views.test_auth_register, name='test_auth_register'),
]