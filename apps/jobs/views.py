from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes

from .models import Job, Company
from .serializers import (
    JobSerializer, JobListSerializer, JobDetailSerializer,
    CompanySerializer, IndustrySerializer, JobTypeSerializer, CategorySerializer
)
from .filters import (
    JobFilter, AdvancedJobSearchFilter, LocationBasedFilter,
    CategoryHierarchyFilter, SalaryRangeFilter, RecentJobsFilter, PopularJobsFilter
)
from apps.categories.models import Industry, JobType, Category

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to create, update, or delete jobs.
    Regular users can only read job data.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed for admin users
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow job creators and admins to edit their jobs.
    Regular users can only read job data.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions require authentication
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed for the job creator or admin users
        return obj.created_by == request.user or request.user.is_admin


@extend_schema_view(
    list=extend_schema(
        tags=['Jobs'],
        summary='List all active jobs',
        description='Get a paginated list of all active job postings with filtering and search capabilities',
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in job title, description, company name, location, or required skills'
            ),
            OpenApiParameter(
                name='industry',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by industry ID'
            ),
            OpenApiParameter(
                name='job_type',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by job type ID'
            ),
            OpenApiParameter(
                name='location',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by location'
            ),
            OpenApiParameter(
                name='salary_min',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Minimum salary filter'
            ),
            OpenApiParameter(
                name='salary_max',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum salary filter'
            ),
            OpenApiParameter(
                name='categories',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by category IDs (comma-separated)'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order by: created_at, updated_at, title, salary_min, salary_max, views_count, applications_count (prefix with - for descending)'
            ),
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Page number for pagination'
            ),
            OpenApiParameter(
                name='include_inactive',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Include inactive jobs (admin only)'
            )
        ],
        responses={
            200: OpenApiResponse(
                description='List of jobs retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Jobs List Response',
                        value={
                            'count': 150,
                            'next': 'http://localhost:8000/api/jobs/?page=2',
                            'previous': None,
                            'results': [
                                {
                                    'id': 1,
                                    'title': 'Senior Software Engineer',
                                    'company': {
                                        'id': 1,
                                        'name': 'Tech Corp',
                                        'logo': 'http://example.com/logo.png'
                                    },
                                    'location': 'San Francisco, CA',
                                    'salary_min': 120000,
                                    'salary_max': 180000,
                                    'job_type': {
                                        'id': 1,
                                        'name': 'Full-time'
                                    },
                                    'industry': {
                                        'id': 1,
                                        'name': 'Technology'
                                    },
                                    'categories': [
                                        {
                                            'id': 1,
                                            'name': 'Software Development',
                                            'slug': 'software-development'
                                        }
                                    ],
                                    'is_featured': False,
                                    'created_at': '2024-01-15T10:30:00Z',
                                    'views_count': 245,
                                    'applications_count': 12
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
        tags=['Jobs'],
        summary='Create new job posting',
        description='Create a new job posting (admin only)',
        examples=[
            OpenApiExample(
                'Job Creation Example',
                value={
                    'title': 'Senior Software Engineer',
                    'description': 'We are looking for an experienced software engineer...',
                    'company': 1,
                    'location': 'San Francisco, CA',
                    'salary_min': 120000,
                    'salary_max': 180000,
                    'job_type': 1,
                    'industry': 1,
                    'categories': [1, 2],
                    'required_skills': 'Python, Django, PostgreSQL, React',
                    'experience_required': 'Senior',
                    'education_required': 'Bachelor\'s degree in Computer Science or related field',
                    'benefits': 'Health insurance, 401k, flexible hours',
                    'application_deadline': '2024-03-15T23:59:59Z'
                },
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(
                description='Job created successfully',
                examples=[
                    OpenApiExample(
                        'Job Created Response',
                        value={
                            'id': 1,
                            'title': 'Senior Software Engineer',
                            'description': 'We are looking for an experienced software engineer...',
                            'company': {
                                'id': 1,
                                'name': 'Tech Corp',
                                'description': 'Leading technology company',
                                'logo': 'http://example.com/logo.png'
                            },
                            'location': 'San Francisco, CA',
                            'salary_min': 120000,
                            'salary_max': 180000,
                            'job_type': {
                                'id': 1,
                                'name': 'Full-time'
                            },
                            'industry': {
                                'id': 1,
                                'name': 'Technology'
                            },
                            'categories': [
                                {
                                    'id': 1,
                                    'name': 'Software Development',
                                    'slug': 'software-development'
                                }
                            ],
                            'required_skills': 'Python, Django, PostgreSQL, React',
                            'is_active': True,
                            'is_featured': False,
                            'created_at': '2024-01-15T10:30:00Z',
                            'created_by': {
                                'id': 1,
                                'email': 'admin@example.com',
                                'first_name': 'Admin',
                                'last_name': 'User'
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Validation error',
                examples=[
                    OpenApiExample(
                        'Validation Error',
                        value={
                            'title': ['This field is required.'],
                            'salary_min': ['Ensure this value is greater than 0.']
                        }
                    )
                ]
            ),
            403: OpenApiResponse(
                description='Admin permission required',
                examples=[
                    OpenApiExample(
                        'Permission Denied',
                        value={'error': 'Only administrators can create job postings.'}
                    )
                ]
            )
        }
    ),
    retrieve=extend_schema(
        tags=['Jobs'],
        summary='Get job details',
        description='Retrieve detailed information about a specific job posting',
        responses={
            200: OpenApiResponse(
                description='Job details retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Job Details Response',
                        value={
                            'id': 1,
                            'title': 'Senior Software Engineer',
                            'description': 'We are looking for an experienced software engineer...',
                            'company': {
                                'id': 1,
                                'name': 'Tech Corp',
                                'description': 'Leading technology company',
                                'logo': 'http://example.com/logo.png',
                                'website': 'https://techcorp.com',
                                'employee_count': '1000-5000'
                            },
                            'location': 'San Francisco, CA',
                            'salary_min': 120000,
                            'salary_max': 180000,
                            'job_type': {
                                'id': 1,
                                'name': 'Full-time',
                                'description': 'Full-time employment'
                            },
                            'industry': {
                                'id': 1,
                                'name': 'Technology',
                                'description': 'Technology and software industry'
                            },
                            'categories': [
                                {
                                    'id': 1,
                                    'name': 'Software Development',
                                    'slug': 'software-development',
                                    'description': 'Software development positions'
                                }
                            ],
                            'required_skills': 'Python, Django, PostgreSQL, React',
                            'experience_required': 'Senior',
                            'education_required': 'Bachelor\'s degree in Computer Science',
                            'benefits': 'Health insurance, 401k, flexible hours',
                            'application_deadline': '2024-03-15T23:59:59Z',
                            'is_active': True,
                            'is_featured': False,
                            'views_count': 245,
                            'applications_count': 12,
                            'created_at': '2024-01-15T10:30:00Z',
                            'updated_at': '2024-01-15T10:30:00Z',
                            'created_by': {
                                'id': 1,
                                'email': 'admin@example.com',
                                'first_name': 'Admin',
                                'last_name': 'User'
                            }
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description='Job not found',
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
        tags=['Jobs'],
        summary='Update job posting',
        description='Update a job posting (admin or job creator only)',
        responses={
            200: OpenApiResponse(description='Job updated successfully'),
            403: OpenApiResponse(
                description='Permission denied',
                examples=[
                    OpenApiExample(
                        'Permission Denied',
                        value={'error': 'You do not have permission to update this job.'}
                    )
                ]
            ),
            404: OpenApiResponse(description='Job not found')
        }
    ),
    partial_update=extend_schema(
        tags=['Jobs'],
        summary='Partially update job posting',
        description='Partially update a job posting (admin or job creator only)',
        responses={
            200: OpenApiResponse(description='Job updated successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Job not found')
        }
    ),
    destroy=extend_schema(
        tags=['Jobs'],
        summary='Delete job posting',
        description='Delete (deactivate) a job posting (admin or job creator only)',
        responses={
            204: OpenApiResponse(
                description='Job deactivated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={'message': 'Job posting has been deactivated successfully.'}
                    )
                ]
            ),
            403: OpenApiResponse(
                description='Permission denied',
                examples=[
                    OpenApiExample(
                        'Permission Denied',
                        value={'error': 'You do not have permission to delete this job.'}
                    )
                ]
            ),
            404: OpenApiResponse(description='Job not found')
        }
    )
)
class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job postings with CRUD operations.
    
    Provides:
    - list: Get paginated list of active jobs
    - create: Create new job (admin only)
    - retrieve: Get detailed job information
    - update: Update job (admin or job creator only)
    - partial_update: Partially update job (admin or job creator only)
    - destroy: Delete job (admin or job creator only)
    """
    
    queryset = Job.objects.select_related(
        'company', 'industry', 'job_type', 'created_by', 'updated_by'
    ).prefetch_related('categories').filter(is_active=True)
    
    permission_classes = [IsAuthenticated, IsOwnerOrAdminOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        AdvancedJobSearchFilter,
        LocationBasedFilter,
        CategoryHierarchyFilter,
        SalaryRangeFilter,
        RecentJobsFilter,
        PopularJobsFilter,
        SearchFilter,
        OrderingFilter
    ]
    
    # Use custom filter class
    filterset_class = JobFilter
    
    # Search fields (fallback for basic search)
    search_fields = ['title', 'description', 'company__name', 'location', 'required_skills']
    
    # Ordering options
    ordering_fields = ['created_at', 'updated_at', 'title', 'salary_min', 'salary_max', 'views_count', 'applications_count']
    ordering = ['-created_at']  # Default ordering
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        """
        if self.action == 'list':
            return JobListSerializer
        elif self.action == 'retrieve':
            return JobDetailSerializer
        return JobSerializer
    
    def get_queryset(self):
        """
        Optionally restricts the returned jobs based on query parameters.
        """
        queryset = self.queryset
        
        # Allow admins to see inactive jobs with a query parameter
        if self.request.user.is_admin and self.request.query_params.get('include_inactive'):
            queryset = Job.objects.select_related(
                'company', 'industry', 'job_type', 'created_by', 'updated_by'
            ).prefetch_related('categories').all()
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        List jobs with pagination and filtering.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new job posting (admin only).
        """
        # Check admin permission explicitly
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can create job postings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # The serializer will set created_by and updated_by from request context
        job = serializer.save()
        
        # Return detailed job data
        detail_serializer = JobDetailSerializer(job)
        headers = self.get_success_headers(detail_serializer.data)
        
        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific job and increment view count.
        """
        instance = self.get_object()
        
        # Increment view count (async in production)
        instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Update a job posting (admin or job creator only).
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check permissions
        if not (request.user.is_admin or instance.created_by == request.user):
            return Response(
                {'error': 'You do not have permission to update this job.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        job = serializer.save()
        
        # Return detailed job data
        detail_serializer = JobDetailSerializer(job)
        return Response(detail_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a job posting (admin or job creator only).
        """
        instance = self.get_object()
        
        # Check permissions
        if not (request.user.is_admin or instance.created_by == request.user):
            return Response(
                {'error': 'You do not have permission to delete this job.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete by setting is_active to False
        instance.is_active = False
        instance.updated_by = request.user
        instance.save(update_fields=['is_active', 'updated_by', 'updated_at'])
        
        return Response(
            {'message': 'Job posting has been deactivated successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle_featured(self, request, pk=None):
        """
        Toggle featured status of a job (admin only).
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can feature jobs.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        job = self.get_object()
        job.is_featured = not job.is_featured
        job.updated_by = request.user
        job.save(update_fields=['is_featured', 'updated_by', 'updated_at'])
        
        return Response({
            'message': f'Job {"featured" if job.is_featured else "unfeatured"} successfully.',
            'is_featured': job.is_featured
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reactivate(self, request, pk=None):
        """
        Reactivate a deactivated job (admin or job creator only).
        """
        # Get job including inactive ones
        try:
            job = Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Job not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        if not (request.user.is_admin or job.created_by == request.user):
            return Response(
                {'error': 'You do not have permission to reactivate this job.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if job.is_active:
            return Response(
                {'error': 'Job is already active.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        job.is_active = True
        job.updated_by = request.user
        job.save(update_fields=['is_active', 'updated_by', 'updated_at'])
        
        return Response({
            'message': 'Job has been reactivated successfully.',
            'is_active': job.is_active
        })
    
    @extend_schema(
        tags=['Jobs'],
        summary='Advanced job search',
        description='Search jobs with advanced filtering and ranking capabilities',
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search query for job title, description, company name, or skills'
            ),
            OpenApiParameter(
                name='location',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Location filter'
            ),
            OpenApiParameter(
                name='industry',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Industry ID filter'
            ),
            OpenApiParameter(
                name='job_type',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Job type ID filter'
            ),
            OpenApiParameter(
                name='salary_min',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Minimum salary filter'
            ),
            OpenApiParameter(
                name='salary_max',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum salary filter'
            )
        ],
        responses={
            200: OpenApiResponse(
                description='Search results retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Search Results',
                        value={
                            'count': 25,
                            'next': None,
                            'previous': None,
                            'results': [
                                {
                                    'id': 1,
                                    'title': 'Senior Software Engineer',
                                    'company': {
                                        'id': 1,
                                        'name': 'Tech Corp',
                                        'logo': 'http://example.com/logo.png'
                                    },
                                    'location': 'San Francisco, CA',
                                    'salary_min': 120000,
                                    'salary_max': 180000,
                                    'job_type': {
                                        'id': 1,
                                        'name': 'Full-time'
                                    },
                                    'created_at': '2024-01-15T10:30:00Z'
                                }
                            ]
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def search(self, request):
        """
        Advanced search endpoint with multiple search criteria.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply additional search logic if needed
        search_query = request.query_params.get('q')
        if search_query:
            # Enhanced search with ranking could be implemented here
            # For now, use the existing filter backends
            pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        tags=['Jobs'],
        summary='Get featured jobs',
        description='Retrieve a list of featured job postings',
        responses={
            200: OpenApiResponse(
                description='Featured jobs retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Featured Jobs Response',
                        value={
                            'count': 10,
                            'next': None,
                            'previous': None,
                            'results': [
                                {
                                    'id': 1,
                                    'title': 'Senior Software Engineer',
                                    'company': {
                                        'id': 1,
                                        'name': 'Tech Corp',
                                        'logo': 'http://example.com/logo.png'
                                    },
                                    'location': 'San Francisco, CA',
                                    'salary_min': 120000,
                                    'salary_max': 180000,
                                    'is_featured': True,
                                    'created_at': '2024-01-15T10:30:00Z'
                                }
                            ]
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def featured(self, request):
        """
        Get featured jobs.
        """
        queryset = self.get_queryset().filter(is_featured=True)
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recent(self, request):
        """
        Get recently posted jobs (last 7 days by default).
        """
        from django.utils import timezone
        from datetime import timedelta
        
        days = int(request.query_params.get('days', 7))
        cutoff_date = timezone.now() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(created_at__gte=cutoff_date)
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def popular(self, request):
        """
        Get popular jobs based on views and applications.
        """
        from django.db.models import F
        
        # Order by a combination of views and applications
        queryset = self.get_queryset().annotate(
            popularity_score=F('views_count') + F('applications_count') * 2
        ).order_by('-popularity_score', '-created_at')
        
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def similar(self, request):
        """
        Find similar jobs based on a reference job ID.
        """
        reference_job_id = request.query_params.get('job_id')
        if not reference_job_id:
            return Response(
                {'error': 'job_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reference_job = Job.objects.get(id=reference_job_id, is_active=True)
        except Job.DoesNotExist:
            return Response(
                {'error': 'Reference job not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find similar jobs based on industry, job_type, and categories
        similar_jobs = self.get_queryset().filter(
            Q(industry=reference_job.industry) |
            Q(job_type=reference_job.job_type) |
            Q(categories__in=reference_job.categories.all())
        ).exclude(id=reference_job.id).distinct()
        
        # Order by relevance (jobs with more matching criteria first)
        queryset = self.filter_queryset(similar_jobs)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = JobListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobListSerializer(queryset, many=True)
        return Response(serializer.data)


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for company information (read-only for regular users).
    """
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['founded_year', 'employee_count']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'founded_year']
    ordering = ['name']


class IndustryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for industry information (read-only).
    """
    queryset = Industry.objects.filter(is_active=True)
    serializer_class = IndustrySerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class JobTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for job type information (read-only).
    """
    queryset = JobType.objects.filter(is_active=True)
    serializer_class = JobTypeSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for category information (read-only).
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, pk=None):
        """
        Get all jobs in this category and its subcategories.
        """
        category = self.get_object()
        
        # Get jobs directly in this category and all descendant categories
        descendant_categories = [category] + category.get_descendants()
        jobs = Job.objects.filter(
            categories__in=descendant_categories,
            is_active=True
        ).distinct().select_related(
            'company', 'industry', 'job_type'
        ).prefetch_related('categories')
        
        # Apply pagination
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = JobListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = JobListSerializer(jobs, many=True)
        return Response(serializer.data)
