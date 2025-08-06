"""
Categories app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, IndustryViewSet, JobTypeViewSet

app_name = 'categories'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'industries', IndustryViewSet, basename='industry')
router.register(r'job-types', JobTypeViewSet, basename='jobtype')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]