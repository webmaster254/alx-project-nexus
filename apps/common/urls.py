"""
URL configuration for common app.
"""

from django.urls import path
from . import health

app_name = 'common'

urlpatterns = [
    # Health check endpoints
    path('health/', health.health_check, name='health_check'),
    path('health/live/', health.liveness_probe, name='liveness_probe'),
    path('health/ready/', health.readiness_probe, name='readiness_probe'),
    path('metrics/', health.metrics, name='metrics'),
]