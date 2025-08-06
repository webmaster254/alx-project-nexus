"""
Common permission classes for the application.
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Regular users have read-only access.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed for admin users
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    
    def has_permission(self, request, view):
        # Permission is granted to authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin
        if request.user.is_admin:
            return True
        
        # Check if the object has a user field (for applications)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object has an application field with user (for documents)
        if hasattr(obj, 'application') and hasattr(obj.application, 'user'):
            return obj.application.user == request.user
        
        # Default to False if we can't determine ownership
        return False


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if the object has an application field with user
        if hasattr(obj, 'application') and hasattr(obj.application, 'user'):
            return obj.application.user == request.user
        
        # Default to False if we can't determine ownership
        return False