"""
Application views for handling job application API endpoints.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
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


@extend_schema_view(
    list=extend_schema(
        tags=['Applications'],
        summary='List job applications',
        description='Get a paginated list of job applications. Regular users see only their own applications, admins see all applications.',
        parameters=[
            OpenApiParameter(
                name='status__name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by application status (pending, reviewed, accepted, rejected, withdrawn)'
            ),
            OpenApiParameter(
                name='job__id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by job ID'
            ),
            OpenApiParameter(
                name='job__company__id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by company ID'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in job title, company name, or cover letter'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order by: applied_at, updated_at, status__name (prefix with - for descending)'
            )
        ],
        responses={
            200: OpenApiResponse(
                description='Applications retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Applications List Response',
                        value={
                            'count': 25,
                            'next': 'http://localhost:8000/api/applications/?page=2',
                            'previous': None,
                            'results': [
                                {
                                    'id': 1,
                                    'job': {
                                        'id': 1,
                                        'title': 'Senior Software Engineer',
                                        'company': {
                                            'id': 1,
                                            'name': 'Tech Corp',
                                            'logo': 'http://example.com/logo.png'
                                        },
                                        'location': 'San Francisco, CA',
                                        'salary_min': 120000,
                                        'salary_max': 180000
                                    },
                                    'status': {
                                        'id': 1,
                                        'name': 'pending',
                                        'display_name': 'Pending Review',
                                        'description': 'Application is pending review'
                                    },
                                    'user_email': 'user@example.com',
                                    'user_full_name': 'John Doe',
                                    'applied_at': '2024-01-15T10:30:00Z',
                                    'days_since_applied': 5,
                                    'is_recent': True,
                                    'can_withdraw': True
                                }
                            ]
                        }
                    )
                ]
            ),
            401: OpenApiResponse(
                description='Authentication required',
                examples=[
                    OpenApiExample(
                        'Unauthorized',
                        value={'detail': 'Authentication credentials were not provided.'}
                    )
                ]
            )
        }
    ),
    create=extend_schema(
        tags=['Applications'],
        summary='Submit job application',
        description='Submit a new job application. Prevents duplicate applications for the same job.',
        examples=[
            OpenApiExample(
                'Application Submission Example',
                value={
                    'job': 1,
                    'cover_letter': 'I am very interested in this position because...',
                    'documents': [
                        {
                            'document_type': 'resume',
                            'title': 'My Resume',
                            'file': 'base64_encoded_file_content'
                        }
                    ]
                },
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(
                description='Application submitted successfully',
                examples=[
                    OpenApiExample(
                        'Application Created Response',
                        value={
                            'id': 1,
                            'job': {
                                'id': 1,
                                'title': 'Senior Software Engineer',
                                'company': {
                                    'id': 1,
                                    'name': 'Tech Corp',
                                    'description': 'Leading technology company',
                                    'logo': 'http://example.com/logo.png'
                                },
                                'location': 'San Francisco, CA',
                                'salary_min': 120000,
                                'salary_max': 180000
                            },
                            'user': {
                                'id': 1,
                                'email': 'user@example.com',
                                'first_name': 'John',
                                'last_name': 'Doe'
                            },
                            'status': {
                                'id': 1,
                                'name': 'pending',
                                'display_name': 'Pending Review',
                                'description': 'Application is pending review'
                            },
                            'cover_letter': 'I am very interested in this position because...',
                            'applied_at': '2024-01-15T10:30:00Z',
                            'updated_at': '2024-01-15T10:30:00Z',
                            'documents': [
                                {
                                    'id': 1,
                                    'document_type': 'resume',
                                    'title': 'My Resume',
                                    'file': 'http://example.com/media/documents/resume.pdf',
                                    'file_size': 1024000,
                                    'uploaded_at': '2024-01-15T10:30:00Z'
                                }
                            ]
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Validation error or duplicate application',
                examples=[
                    OpenApiExample(
                        'Duplicate Application',
                        value={
                            'non_field_errors': ['You have already applied for this job.']
                        }
                    ),
                    OpenApiExample(
                        'Validation Error',
                        value={
                            'job': ['This field is required.'],
                            'cover_letter': ['This field may not be blank.']
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description='Job not found',
                examples=[
                    OpenApiExample(
                        'Job Not Found',
                        value={'job': ['Invalid pk "999" - object does not exist.']}
                    )
                ]
            )
        }
    ),
    retrieve=extend_schema(
        tags=['Applications'],
        summary='Get application details',
        description='Retrieve detailed information about a specific application. Users can only view their own applications unless they are admin.',
        responses={
            200: OpenApiResponse(
                description='Application details retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Application Details Response',
                        value={
                            'id': 1,
                            'job': {
                                'id': 1,
                                'title': 'Senior Software Engineer',
                                'company': {
                                    'id': 1,
                                    'name': 'Tech Corp',
                                    'description': 'Leading technology company',
                                    'logo': 'http://example.com/logo.png',
                                    'website': 'https://techcorp.com'
                                },
                                'location': 'San Francisco, CA',
                                'salary_min': 120000,
                                'salary_max': 180000,
                                'job_type': {
                                    'id': 1,
                                    'name': 'Full-time'
                                }
                            },
                            'user': {
                                'id': 1,
                                'email': 'user@example.com',
                                'first_name': 'John',
                                'last_name': 'Doe'
                            },
                            'status': {
                                'id': 2,
                                'name': 'reviewed',
                                'display_name': 'Under Review',
                                'description': 'Application is being reviewed by the hiring team'
                            },
                            'cover_letter': 'I am very interested in this position because...',
                            'applied_at': '2024-01-15T10:30:00Z',
                            'updated_at': '2024-01-16T14:20:00Z',
                            'reviewed_by': {
                                'id': 2,
                                'email': 'admin@example.com',
                                'first_name': 'Admin',
                                'last_name': 'User'
                            },
                            'notes': 'Strong technical background, proceeding to next round',
                            'documents': [
                                {
                                    'id': 1,
                                    'document_type': 'resume',
                                    'title': 'My Resume',
                                    'file': 'http://example.com/media/documents/resume.pdf',
                                    'file_size': 1024000,
                                    'file_size_display': '1.0 MB',
                                    'file_extension': 'pdf',
                                    'uploaded_at': '2024-01-15T10:30:00Z'
                                }
                            ]
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description='Permission denied',
                examples=[
                    OpenApiExample(
                        'Permission Denied',
                        value={'detail': 'You do not have permission to perform this action.'}
                    )
                ]
            ),
            404: OpenApiResponse(
                description='Application not found',
                examples=[
                    OpenApiExample(
                        'Not Found',
                        value={'detail': 'Not found.'}
                    )
                ]
            )
        }
    ),
    update=extend_schema(
        tags=['Applications'],
        summary='Update application status',
        description='Update application status and add review notes (admin only)',
        examples=[
            OpenApiExample(
                'Status Update Example',
                value={
                    'status': 2,
                    'notes': 'Candidate has strong technical skills, moving to interview stage'
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                description='Application updated successfully',
                examples=[
                    OpenApiExample(
                        'Updated Application Response',
                        value={
                            'id': 1,
                            'status': {
                                'id': 2,
                                'name': 'reviewed',
                                'display_name': 'Under Review'
                            },
                            'notes': 'Candidate has strong technical skills, moving to interview stage',
                            'updated_at': '2024-01-16T14:20:00Z',
                            'reviewed_by': {
                                'id': 2,
                                'email': 'admin@example.com',
                                'first_name': 'Admin',
                                'last_name': 'User'
                            }
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description='Admin permission required',
                examples=[
                    OpenApiExample(
                        'Permission Denied',
                        value={'detail': 'You do not have permission to perform this action.'}
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid status transition',
                examples=[
                    OpenApiExample(
                        'Invalid Status',
                        value={'status': ['Cannot change status from accepted to pending.']}
                    )
                ]
            )
        }
    ),
    destroy=extend_schema(
        tags=['Applications'],
        summary='Delete application',
        description='Delete an application (admin only). This is a hard delete and cannot be undone.',
        responses={
            204: OpenApiResponse(
                description='Application deleted successfully'
            ),
            403: OpenApiResponse(
                description='Admin permission required',
                examples=[
                    OpenApiExample(
                        'Permission Denied',
                        value={'detail': 'You do not have permission to perform this action.'}
                    )
                ]
            ),
            404: OpenApiResponse(
                description='Application not found'
            )
        }
    )
)
class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job applications.
    Provides user-specific application listing and submission functionality.
    
    **Authentication Required**: All endpoints require JWT authentication.
    
    **Permissions**:
    - Regular users can view and create their own applications
    - Admins can view all applications and update statuses
    - Only admins can delete applications
    
    **Available Actions**:
    - `list`: Get paginated list of applications
    - `create`: Submit new job application
    - `retrieve`: Get detailed application information
    - `update`: Update application status (admin only)
    - `destroy`: Delete application (admin only)
    - `withdraw`: Withdraw application (user action)
    - `my_applications`: Get current user's applications
    - `statistics`: Get application statistics
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
    
    @extend_schema(
        tags=['Applications'],
        summary='Withdraw job application',
        description='Withdraw a job application. Only the application owner can withdraw their own application.',
        responses={
            200: OpenApiResponse(
                description='Application withdrawn successfully',
                examples=[
                    OpenApiExample(
                        'Withdrawn Application Response',
                        value={
                            'id': 1,
                            'status': {
                                'id': 5,
                                'name': 'withdrawn',
                                'display_name': 'Withdrawn',
                                'description': 'Application has been withdrawn by the applicant'
                            },
                            'updated_at': '2024-01-16T14:20:00Z',
                            'notes': 'Application withdrawn by user'
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description='Permission denied',
                examples=[
                    OpenApiExample(
                        'Permission Denied',
                        value={'error': 'You can only withdraw your own applications.'}
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Cannot withdraw application',
                examples=[
                    OpenApiExample(
                        'Cannot Withdraw',
                        value={'error': 'Cannot withdraw application that has already been processed.'}
                    )
                ]
            )
        }
    )
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
    
    @extend_schema(
        tags=['Applications'],
        summary='Get my applications',
        description='Retrieve all applications submitted by the current user with filtering and pagination.',
        parameters=[
            OpenApiParameter(
                name='status__name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by application status'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order by: applied_at, updated_at, status__name'
            )
        ],
        responses={
            200: OpenApiResponse(
                description='User applications retrieved successfully',
                examples=[
                    OpenApiExample(
                        'My Applications Response',
                        value={
                            'count': 5,
                            'next': None,
                            'previous': None,
                            'results': [
                                {
                                    'id': 1,
                                    'job': {
                                        'id': 1,
                                        'title': 'Senior Software Engineer',
                                        'company': {
                                            'id': 1,
                                            'name': 'Tech Corp'
                                        }
                                    },
                                    'status': {
                                        'id': 1,
                                        'name': 'pending',
                                        'display_name': 'Pending Review'
                                    },
                                    'applied_at': '2024-01-15T10:30:00Z',
                                    'can_withdraw': True
                                }
                            ]
                        }
                    )
                ]
            )
        }
    )
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
    
    @extend_schema(
        tags=['Applications'],
        summary='Get application statistics',
        description='Retrieve application statistics. Regular users see their own stats, admins see global statistics.',
        responses={
            200: OpenApiResponse(
                description='Statistics retrieved successfully',
                examples=[
                    OpenApiExample(
                        'User Statistics Response',
                        value={
                            'total_applications': 12,
                            'status_breakdown': {
                                'pending': 3,
                                'reviewed': 2,
                                'accepted': 1,
                                'rejected': 5,
                                'withdrawn': 1
                            },
                            'recent_applications_30_days': 8
                        }
                    ),
                    OpenApiExample(
                        'Admin Statistics Response',
                        value={
                            'total_applications': 1250,
                            'status_breakdown': {
                                'pending': 150,
                                'reviewed': 300,
                                'accepted': 200,
                                'rejected': 500,
                                'withdrawn': 100
                            },
                            'recent_applications_30_days': 350
                        }
                    )
                ]
            )
        }
    )
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
