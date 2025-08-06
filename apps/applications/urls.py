"""
Applications app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.applications.views import ApplicationViewSet, ApplicationStatusViewSet, DocumentViewSet

app_name = 'applications'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'application-statuses', ApplicationStatusViewSet, basename='applicationstatus')
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]