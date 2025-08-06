"""
Application views for handling job application API endpoints.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Q
from apps.applications.models import Application, ApplicationStatus, Document
from apps.applications.serializers import (
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationCreateSerializer,
    ApplicationUpdateSerializer,
    ApplicationWithdrawSerializer,
    BulkStatusUpdateSerializer,
    ApplicationStatusListSerializer,
    DocumentSerializer
)
from apps.common.permissions import IsAdminOrReadOnly, IsOwnerOrAdmin, IsAdminUser


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job applications.
    Provides user-specific application listing and submission functionality.
    """
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['status__name', 'job__id', 'job__company__id']
    ordering_fields = ['applied_at', 'updated_at', 'status__name']
    ordering = ['-applied_at']
    search_fields = ['job__title', 'job__company__name', 'cover_letter']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return applications based on user role.
        Regular users see only their own applications.
        Admins see all applications.
        """
        user = self.request.user
        
        if user.is_admin:
            # Admins can see all applications
            queryset = Application.objects.select_related(
                'user', 'job', 'job__company', 'status', 'reviewed_by'
            ).prefetch_related('documents')
        else:
            # Regular users see only their own applications
            queryset = Application.objects.filter(user=user).select_related(
                'job', 'job__company', 'status', 'reviewed_by'
            ).prefetch_related('documents')
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ApplicationListSerializer
        elif self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ApplicationUpdateSerializer
        elif self.action == 'withdraw':
            return ApplicationWithdrawSerializer
        else:
            return ApplicationDetailSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['update', 'partial_update']:
            # Only admins can update application status
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        elif self.action == 'destroy':
            # Only admins can delete applications
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        elif self.action == 'withdraw':
            # Only the application owner can withdraw
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        else:
            # Default: authenticated users
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new job application with duplicate prevention.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the application
        application = serializer.save()
        
        # Return detailed application data
        response_serializer = ApplicationDetailSerializer(
            application, context={'request': request}
        )
        
        return Response(
            response_serializer.data, 
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """
        Update application status (admin only).
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Update the application
        application = serializer.save()
        
        # Return detailed application data
        response_serializer = ApplicationDetailSerializer(
            application, context={'request': request}
        )
        
        return Response(response_serializer.data)
    
    @action(detail=True, methods=['post'], url_path='withdraw')
    def withdraw(self, request, pk=None):
        """
        Withdraw an application (user action).
        Only the application owner can withdraw their application.
        """
        application = self.get_object()
        
        # Check if user owns the application
        if not request.user.is_admin and application.user != request.user:
            return Response(
                {'error': 'You can only withdraw your own applications.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(application, data={})
        serializer.is_valid(raise_exception=True)
        
        # Withdraw the application
        withdrawn_application = serializer.save()
        
        # Return updated application data
        response_serializer = ApplicationDetailSerializer(
            withdrawn_application, context={'request': request}
        )
        
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['get'], url_path='my-applications')
    def my_applications(self, request):
        """
        Get current user's applications.
        """
        queryset = self.get_queryset().filter(user=request.user)
        
        # Apply filters
        queryset = self.filter_queryset(queryset)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ApplicationListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ApplicationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-status/(?P<status_name>[^/.]+)')
    def by_status(self, request, status_name=None):
        """
        Get applications filtered by status.
        """
        try:
            status_obj = ApplicationStatus.objects.get(name=status_name)
        except ApplicationStatus.DoesNotExist:
            return Response(
                {'error': f'Status "{status_name}" not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        queryset = self.get_queryset().filter(status=status_obj)
        
        # Apply additional filters
        queryset = self.filter_queryset(queryset)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ApplicationListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ApplicationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-job/(?P<job_id>[^/.]+)', 
            permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def by_job(self, request, job_id=None):
        """
        Get applications filtered by job (admin only).
        """
        from apps.jobs.models import Job
        
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response(
                {'error': f'Job with ID "{job_id}" not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        queryset = self.get_queryset().filter(job=job)
        
        # Apply additional filters
        queryset = self.filter_queryset(queryset)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ApplicationListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ApplicationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='admin/pending', 
            permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def admin_pending(self, request):
        """
        Get all pending applications for admin review.
        """
        queryset = self.get_queryset().filter(status__name='pending')
        
        # Apply additional filters
        queryset = self.filter_queryset(queryset)
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ApplicationListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ApplicationListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='update-status',
            permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def update_status(self, request, pk=None):
        """
        Update application status (admin only).
        Dedicated endpoint for status updates with better validation.
        """
        application = self.get_object()
        
        serializer = ApplicationUpdateSerializer(
            application, 
            data=request.data, 
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Update the application
        updated_application = serializer.save()
        
        # Return detailed application data
        response_serializer = ApplicationDetailSerializer(
            updated_application, context={'request': request}
        )
        
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['post'], url_path='bulk-update-status',
            permission_classes=[permissions.IsAuthenticated, IsAdminUser])
    def bulk_update_status(self, request):
        """
        Bulk update status for multiple applications (admin only).
        """
        application_ids = request.data.get('application_ids', [])
        status_name = request.data.get('status_name')
        notes = request.data.get('notes', '')
        
        if not application_ids:
            return Response(
                {'error': 'application_ids is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not status_name:
            return Response(
                {'error': 'status_name is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate status exists
        try:
            new_status = ApplicationStatus.objects.get(name=status_name)
        except ApplicationStatus.DoesNotExist:
            return Response(
                {'error': f'Status "{status_name}" not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get applications that can be updated
        applications = self.get_queryset().filter(
            id__in=application_ids
        ).exclude(status__is_final=True)
        
        if not applications.exists():
            return Response(
                {'error': 'No valid applications found for update.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update applications
        updated_count = 0
        updated_applications = []
        
        for application in applications:
            try:
                application.update_status(
                    new_status=new_status,
                    reviewed_by=request.user,
                    notes=notes
                )
                updated_count += 1
                updated_applications.append(application)
            except Exception as e:
                # Skip applications that can't be updated
                continue
        
        # Return summary
        return Response({
            'message': f'Successfully updated {updated_count} applications.',
            'updated_count': updated_count,
            'total_requested': len(application_ids),
            'updated_applications': [app.id for app in updated_applications]
        })
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Get application statistics for the current user or all applications (admin).
        """
        queryset = self.get_queryset()
        
        # Calculate statistics
        total_applications = queryset.count()
        pending_count = queryset.filter(status__name='pending').count()
        reviewed_count = queryset.filter(status__name='reviewed').count()
        accepted_count = queryset.filter(status__name='accepted').count()
        rejected_count = queryset.filter(status__name='rejected').count()
        withdrawn_count = queryset.filter(status__name='withdrawn').count()
        
        # Recent applications (last 30 days)
        from django.utils import timezone
        from datetime import timedelta
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_count = queryset.filter(applied_at__gte=thirty_days_ago).count()
        
        statistics = {
            'total_applications': total_applications,
            'status_breakdown': {
                'pending': pending_count,
                'reviewed': reviewed_count,
                'accepted': accepted_count,
                'rejected': rejected_count,
                'withdrawn': withdrawn_count,
            },
            'recent_applications_30_days': recent_count,
        }
        
        return Response(statistics)


class ApplicationStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing application statuses.
    Provides read-only access to available application statuses.
    """
    queryset = ApplicationStatus.objects.all()
    serializer_class = ApplicationStatusListSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['name']
    
    @action(detail=False, methods=['get'], url_path='available')
    def available(self, request):
        """
        Get all available application statuses.
        """
        statuses = self.get_queryset()
        serializer = self.get_serializer(statuses, many=True)
        return Response(serializer.data)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing application documents.
    """
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['document_type', 'application__id']
    ordering_fields = ['uploaded_at', 'title']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        """
        Return documents based on user role.
        Regular users see only documents from their own applications.
        Admins see all documents.
        """
        user = self.request.user
        
        if user.is_admin:
            # Admins can see all documents
            return Document.objects.select_related('application', 'application__user')
        else:
            # Regular users see only documents from their own applications
            return Document.objects.filter(
                application__user=user
            ).select_related('application')
    
    def get_permissions(self):
        """
        Set permissions based on action.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            # Only document owner or admin can modify/delete
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        else:
            # Default: authenticated users
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Create document and associate with application.
        """
        # Ensure the application belongs to the current user (unless admin)
        application_id = self.request.data.get('application')
        if application_id:
            try:
                application = Application.objects.get(id=application_id)
                if not self.request.user.is_admin and application.user != self.request.user:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("You can only add documents to your own applications.")
            except Application.DoesNotExist:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Application not found.")
        
        serializer.save()
