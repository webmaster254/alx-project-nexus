from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample, OpenApiResponse, OpenApiParameter
from drf_spectacular.openapi import OpenApiTypes
from django.db import models
from .models import Category, Industry, JobType
from .serializers import (
    CategorySerializer, 
    CategoryListSerializer, 
    CategoryHierarchySerializer,
    CategoryWithJobCountSerializer,
    IndustrySerializer, 
    JobTypeSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Read permissions are allowed to any authenticated user.
    """
    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only for admin users
        return request.user.is_authenticated and getattr(request.user, 'is_admin', False)


@extend_schema_view(
    list=extend_schema(
        tags=["Categories"],
        summary="List categories",
        description="Retrieve a list of all active categories with optional filtering and search capabilities.",
        parameters=[
            OpenApiParameter(
                name='parent',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by parent category ID'
            ),
            OpenApiParameter(
                name='parent__slug',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by parent category slug'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in category name and description'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order by: name, created_at, job_count (prefix with - for descending)'
            )
        ],
        responses={
            200: OpenApiResponse(
                description='Categories retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Categories List Response',
                        value={
                            'count': 15,
                            'next': None,
                            'previous': None,
                            'results': [
                                {
                                    'id': 1,
                                    'name': 'Software Development',
                                    'description': 'Software engineering and development positions',
                                    'slug': 'software-development',
                                    'parent': None,
                                    'parent_name': None,
                                    'job_count': 45,
                                    'full_path': 'Software Development',
                                    'level': 0,
                                    'children': [
                                        {
                                            'id': 2,
                                            'name': 'Frontend Development',
                                            'slug': 'frontend-development',
                                            'job_count': 15
                                        }
                                    ],
                                    'is_active': True,
                                    'created_at': '2024-01-10T10:00:00Z'
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
        tags=["Categories"],
        summary="Create category",
        description="Create a new category. Admin access required.",
        examples=[
            OpenApiExample(
                'Category Creation Example',
                value={
                    'name': 'Data Science',
                    'description': 'Data science and analytics positions',
                    'parent': 1
                },
                request_only=True
            )
        ],
        responses={
            201: OpenApiResponse(
                description='Category created successfully',
                examples=[
                    OpenApiExample(
                        'Category Created Response',
                        value={
                            'id': 3,
                            'name': 'Data Science',
                            'description': 'Data science and analytics positions',
                            'slug': 'data-science',
                            'parent': 1,
                            'parent_name': 'Software Development',
                            'job_count': 0,
                            'full_path': 'Software Development > Data Science',
                            'level': 1,
                            'children': [],
                            'is_active': True,
                            'created_at': '2024-01-15T10:30:00Z'
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
                            'name': ['This field is required.'],
                            'parent': ['Invalid pk "999" - object does not exist.']
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
            )
        }
    ),
    retrieve=extend_schema(
        tags=["Categories"],
        summary="Get category details",
        description="Retrieve detailed information about a specific category by slug.",
        responses={
            200: OpenApiResponse(
                description='Category details retrieved successfully',
                examples=[
                    OpenApiExample(
                        'Category Details Response',
                        value={
                            'id': 1,
                            'name': 'Software Development',
                            'description': 'Software engineering and development positions',
                            'slug': 'software-development',
                            'parent': None,
                            'parent_name': None,
                            'job_count': 45,
                            'full_path': 'Software Development',
                            'level': 0,
                            'children': [
                                {
                                    'id': 2,
                                    'name': 'Frontend Development',
                                    'slug': 'frontend-development',
                                    'job_count': 15
                                },
                                {
                                    'id': 3,
                                    'name': 'Backend Development',
                                    'slug': 'backend-development',
                                    'job_count': 20
                                }
                            ],
                            'is_active': True,
                            'created_at': '2024-01-10T10:00:00Z',
                            'updated_at': '2024-01-10T10:00:00Z'
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description='Category not found',
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
        tags=["Categories"],
        summary="Update category",
        description="Update an existing category. Admin access required.",
        examples=[
            OpenApiExample(
                'Category Update Example',
                value={
                    'name': 'Software Engineering',
                    'description': 'Updated description for software engineering positions'
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                description='Category updated successfully'
            ),
            400: OpenApiResponse(
                description='Validation error'
            ),
            403: OpenApiResponse(
                description='Admin permission required'
            ),
            404: OpenApiResponse(
                description='Category not found'
            )
        }
    ),
    partial_update=extend_schema(
        tags=["Categories"],
        summary="Partially update category",
        description="Partially update an existing category. Admin access required.",
        responses={
            200: OpenApiResponse(description='Category updated successfully'),
            403: OpenApiResponse(description='Admin permission required'),
            404: OpenApiResponse(description='Category not found')
        }
    ),
    destroy=extend_schema(
        tags=["Categories"],
        summary="Delete category",
        description="Soft delete a category by setting is_active to False. Admin access required.",
        responses={
            204: OpenApiResponse(
                description='Category deleted successfully'
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
                description='Category not found'
            )
        }
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories with CRUD operations using slug-based URLs.
    
    - List: GET /api/categories/
    - Create: POST /api/categories/ (admin only)
    - Retrieve: GET /api/categories/{slug}/
    - Update: PUT /api/categories/{slug}/ (admin only)
    - Partial Update: PATCH /api/categories/{slug}/ (admin only)
    - Delete: DELETE /api/categories/{slug}/ (admin only)
    """
    queryset = Category.objects.filter(is_active=True).select_related('parent')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['parent', 'parent__slug']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'job_count']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return CategoryListSerializer
        elif self.action == 'hierarchy':
            return CategoryHierarchySerializer
        return CategorySerializer
    
    def get_queryset(self):
        """Filter queryset based on action and parameters."""
        queryset = super().get_queryset()
        
        # For hierarchy action, only return root categories
        if self.action == 'hierarchy':
            queryset = queryset.filter(parent__isnull=True)
        
        return queryset
    
    @extend_schema(
        summary="Get category hierarchy",
        description="Retrieve categories in a hierarchical structure with nested children.",
        tags=["Categories"]
    )
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """
        Return categories in a hierarchical structure.
        Only returns root categories with nested children.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get category children",
        description="Retrieve direct children of a specific category.",
        tags=["Categories"]
    )
    @action(detail=True, methods=['get'])
    def children(self, request, slug=None):
        """
        Return direct children of a specific category.
        """
        category = self.get_object()
        children = category.children.filter(is_active=True).order_by('name')
        serializer = CategoryListSerializer(children, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get category ancestors",
        description="Retrieve all ancestor categories from root to immediate parent.",
        tags=["Categories"]
    )
    @action(detail=True, methods=['get'])
    def ancestors(self, request, slug=None):
        """
        Return all ancestor categories from root to immediate parent.
        """
        category = self.get_object()
        ancestors = category.get_ancestors()
        serializer = CategoryListSerializer(ancestors, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get category job statistics",
        description="Retrieve detailed job statistics for a specific category including direct and total job counts.",
        tags=["Categories"]
    )
    @action(detail=True, methods=['get'])
    def job_stats(self, request, slug=None):
        """
        Return detailed job statistics for a category.
        """
        category = self.get_object()
        
        # Get direct job count
        direct_jobs = category.jobs.filter(is_active=True).count()
        
        # Get descendant categories and their job counts
        descendants = category.get_descendants()
        descendant_stats = []
        
        for descendant in descendants:
            descendant_jobs = descendant.jobs.filter(is_active=True).count()
            descendant_stats.append({
                'id': descendant.id,
                'name': descendant.name,
                'slug': descendant.slug,
                'job_count': descendant_jobs,
                'level': descendant.get_level()
            })
        
        # Calculate total job count
        total_jobs = direct_jobs + sum(stat['job_count'] for stat in descendant_stats)
        
        return Response({
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'level': category.get_level()
            },
            'direct_job_count': direct_jobs,
            'total_job_count': total_jobs,
            'descendant_categories': descendant_stats
        })
    
    @extend_schema(
        summary="Get jobs in category",
        description="Retrieve all jobs in this category and its subcategories with filtering options.",
        tags=["Categories"]
    )
    @action(detail=True, methods=['get'])
    def jobs(self, request, slug=None):
        """
        Get all jobs in this category and its subcategories.
        """
        from apps.jobs.serializers import JobListSerializer
        from apps.jobs.filters import JobFilter
        from django_filters.rest_framework import DjangoFilterBackend
        
        category = self.get_object()
        
        # Get jobs directly in this category and all descendant categories
        descendant_categories = [category] + category.get_descendants()
        jobs_queryset = category.jobs.model.objects.filter(
            categories__in=descendant_categories,
            is_active=True
        ).distinct().select_related(
            'company', 'industry', 'job_type', 'created_by'
        ).prefetch_related('categories')
        
        # Apply additional filtering if provided
        filter_backend = DjangoFilterBackend()
        filterset = JobFilter(request.query_params, queryset=jobs_queryset)
        if filterset.is_valid():
            jobs_queryset = filterset.qs
        
        # Apply ordering
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering:
            jobs_queryset = jobs_queryset.order_by(ordering)
        
        # Apply pagination
        page = self.paginate_queryset(jobs_queryset)
        if page is not None:
            serializer = JobListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = JobListSerializer(jobs_queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get category tree with job counts",
        description="Retrieve the complete category tree with job count aggregation.",
        tags=["Categories"]
    )
    @action(detail=False, methods=['get'])
    def tree_with_counts(self, request):
        """
        Return the complete category tree with job counts.
        """
        from .serializers import CategoryHierarchySerializer
        
        # Get root categories only
        root_categories = self.get_queryset().filter(parent__isnull=True)
        serializer = CategoryHierarchySerializer(root_categories, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get popular categories",
        description="Retrieve categories ordered by job count (most jobs first).",
        tags=["Categories"]
    )
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Return categories ordered by job count.
        """
        from .serializers import CategoryWithJobCountSerializer
        from django.db.models import Count
        
        # Annotate categories with direct job count and order by it
        queryset = self.get_queryset().annotate(
            direct_job_count=Count('jobs', filter=models.Q(jobs__is_active=True))
        ).order_by('-direct_job_count', 'name')
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CategoryWithJobCountSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CategoryWithJobCountSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def perform_destroy(self, instance):
        """
        Soft delete by setting is_active to False instead of actual deletion.
        This preserves data integrity for jobs that reference this category.
        """
        instance.is_active = False
        instance.save()


@extend_schema_view(
    list=extend_schema(
        summary="List industries",
        description="Retrieve a list of all active industries for job classification.",
        tags=["Industries"]
    ),
    create=extend_schema(
        summary="Create industry",
        description="Create a new industry. Admin access required.",
        tags=["Industries"]
    ),
    retrieve=extend_schema(
        summary="Get industry details",
        description="Retrieve detailed information about a specific industry by slug.",
        tags=["Industries"]
    ),
    update=extend_schema(
        summary="Update industry",
        description="Update an existing industry. Admin access required.",
        tags=["Industries"]
    ),
    partial_update=extend_schema(
        summary="Partially update industry",
        description="Partially update an existing industry. Admin access required.",
        tags=["Industries"]
    ),
    destroy=extend_schema(
        summary="Delete industry",
        description="Delete an industry. Admin access required.",
        tags=["Industries"]
    ),
)
class IndustryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing industries with CRUD operations.
    
    - List: GET /api/industries/
    - Create: POST /api/industries/ (admin only)
    - Retrieve: GET /api/industries/{slug}/
    - Update: PUT /api/industries/{slug}/ (admin only)
    - Partial Update: PATCH /api/industries/{slug}/ (admin only)
    - Delete: DELETE /api/industries/{slug}/ (admin only)
    """
    queryset = Industry.objects.filter(is_active=True)
    serializer_class = IndustrySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'job_count']
    ordering = ['name']
    
    def perform_destroy(self, instance):
        """
        Soft delete by setting is_active to False instead of actual deletion.
        This preserves data integrity for jobs that reference this industry.
        """
        instance.is_active = False
        instance.save()


@extend_schema_view(
    list=extend_schema(
        summary="List job types",
        description="Retrieve a list of all active job types for employment classification.",
        tags=["Job Types"]
    ),
    create=extend_schema(
        summary="Create job type",
        description="Create a new job type. Admin access required.",
        tags=["Job Types"]
    ),
    retrieve=extend_schema(
        summary="Get job type details",
        description="Retrieve detailed information about a specific job type by slug.",
        tags=["Job Types"]
    ),
    update=extend_schema(
        summary="Update job type",
        description="Update an existing job type. Admin access required.",
        tags=["Job Types"]
    ),
    partial_update=extend_schema(
        summary="Partially update job type",
        description="Partially update an existing job type. Admin access required.",
        tags=["Job Types"]
    ),
    destroy=extend_schema(
        summary="Delete job type",
        description="Delete a job type. Admin access required.",
        tags=["Job Types"]
    ),
)
class JobTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing job types with CRUD operations.
    
    - List: GET /api/job-types/
    - Create: POST /api/job-types/ (admin only)
    - Retrieve: GET /api/job-types/{slug}/
    - Update: PUT /api/job-types/{slug}/ (admin only)
    - Partial Update: PATCH /api/job-types/{slug}/ (admin only)
    - Delete: DELETE /api/job-types/{slug}/ (admin only)
    """
    queryset = JobType.objects.filter(is_active=True)
    serializer_class = JobTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'code']
    ordering_fields = ['name', 'created_at', 'job_count']
    ordering = ['name']
    
    def perform_destroy(self, instance):
        """
        Soft delete by setting is_active to False instead of actual deletion.
        This preserves data integrity for jobs that reference this job type.
        """
        instance.is_active = False
        instance.save()
