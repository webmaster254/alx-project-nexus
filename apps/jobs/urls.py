"""
Jobs app URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobViewSet, CompanyViewSet, IndustryViewSet, 
    JobTypeViewSet, CategoryViewSet
)

app_name = 'jobs'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'industries', IndustryViewSet, basename='industry')
router.register(r'job-types', JobTypeViewSet, basename='jobtype')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]