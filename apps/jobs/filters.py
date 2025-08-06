"""
Custom filter backends for job filtering and search functionality.
"""
from django_filters import rest_framework as filters
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend
from .models import Job, Company
from apps.categories.models import Industry, JobType, Category


class JobFilter(filters.FilterSet):
    """
    Advanced filter set for Job model with custom filtering options.
    """
    # Location filtering
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
    location_exact = filters.CharFilter(field_name='location', lookup_expr='exact')
    
    # Salary filtering
    salary_min_gte = filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max_lte = filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    salary_range_min = filters.NumberFilter(method='filter_salary_range_min')
    salary_range_max = filters.NumberFilter(method='filter_salary_range_max')
    
    # Experience level filtering
    experience_level = filters.ChoiceFilter(
        field_name='experience_level',
        choices=Job.EXPERIENCE_LEVELS
    )
    experience_levels = filters.MultipleChoiceFilter(
        field_name='experience_level',
        choices=Job.EXPERIENCE_LEVELS,
        conjoined=False  # OR logic
    )
    
    # Company filtering
    company = filters.ModelChoiceFilter(queryset=Company.objects.filter(is_active=True))
    company_name = filters.CharFilter(field_name='company__name', lookup_expr='icontains')
    
    # Industry and job type filtering
    industry = filters.ModelChoiceFilter(queryset=Industry.objects.filter(is_active=True))
    job_type = filters.ModelChoiceFilter(queryset=JobType.objects.filter(is_active=True))
    
    # Category filtering (supports multiple categories)
    categories = filters.ModelMultipleChoiceFilter(
        queryset=Category.objects.filter(is_active=True),
        conjoined=False  # OR logic - job matches if it has ANY of the specified categories
    )
    category_slug = filters.CharFilter(method='filter_by_category_slug')
    category_slugs = filters.CharFilter(method='filter_by_category_slugs')
    category_hierarchy = filters.NumberFilter(method='filter_by_category_hierarchy')
    category_tree = filters.CharFilter(method='filter_by_category_tree')
    
    # Remote work filtering
    is_remote = filters.BooleanFilter()
    remote_friendly = filters.BooleanFilter(method='filter_remote_friendly')
    
    # Featured jobs
    is_featured = filters.BooleanFilter()
    
    # Date filtering
    posted_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    posted_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    posted_days_ago = filters.NumberFilter(method='filter_posted_days_ago')
    
    # Application deadline filtering
    deadline_after = filters.DateTimeFilter(field_name='application_deadline', lookup_expr='gte')
    deadline_before = filters.DateTimeFilter(field_name='application_deadline', lookup_expr='lte')
    has_deadline = filters.BooleanFilter(method='filter_has_deadline')
    
    # Skills filtering
    required_skills = filters.CharFilter(method='filter_required_skills')
    preferred_skills = filters.CharFilter(method='filter_preferred_skills')
    
    class Meta:
        model = Job
        fields = {
            'salary_type': ['exact'],
            'salary_currency': ['exact'],
            'views_count': ['gte', 'lte'],
            'applications_count': ['gte', 'lte'],
        }
    
    def filter_salary_range_min(self, queryset, name, value):
        """
        Filter jobs where the salary range minimum is at least the specified value.
        Handles cases where only salary_max is specified.
        """
        return queryset.filter(
            Q(salary_min__gte=value) | 
            (Q(salary_min__isnull=True) & Q(salary_max__gte=value))
        )
    
    def filter_salary_range_max(self, queryset, name, value):
        """
        Filter jobs where the salary range maximum is at most the specified value.
        Handles cases where only salary_min is specified.
        """
        return queryset.filter(
            Q(salary_max__lte=value) | 
            (Q(salary_max__isnull=True) & Q(salary_min__lte=value))
        )
    
    def filter_by_category_slug(self, queryset, name, value):
        """Filter jobs by category slug."""
        return queryset.filter(categories__slug=value)
    
    def filter_by_category_slugs(self, queryset, name, value):
        """Filter jobs by multiple category slugs (comma-separated)."""
        if not value:
            return queryset
        
        slugs = [slug.strip() for slug in value.split(',') if slug.strip()]
        if not slugs:
            return queryset
        
        return queryset.filter(categories__slug__in=slugs).distinct()
    
    def filter_by_category_hierarchy(self, queryset, name, value):
        """Filter jobs by category hierarchy (includes all descendant categories)."""
        try:
            category = Category.objects.get(id=value, is_active=True)
            # Get all descendant categories
            descendant_categories = [category] + category.get_descendants()
            return queryset.filter(categories__in=descendant_categories).distinct()
        except Category.DoesNotExist:
            return queryset.none()
    
    def filter_by_category_tree(self, queryset, name, value):
        """Filter jobs by category tree path (e.g., 'technology/software-development')."""
        if not value:
            return queryset
        
        # Split the path and find the deepest category
        path_parts = [part.strip() for part in value.split('/') if part.strip()]
        if not path_parts:
            return queryset
        
        try:
            # Start with root categories
            current_category = None
            for i, slug in enumerate(path_parts):
                if i == 0:
                    # Find root category
                    current_category = Category.objects.get(
                        slug=slug, 
                        parent__isnull=True, 
                        is_active=True
                    )
                else:
                    # Find child category
                    current_category = Category.objects.get(
                        slug=slug, 
                        parent=current_category, 
                        is_active=True
                    )
            
            if current_category:
                # Get all descendant categories
                descendant_categories = [current_category] + current_category.get_descendants()
                return queryset.filter(categories__in=descendant_categories).distinct()
            
        except Category.DoesNotExist:
            pass
        
        return queryset.none()
    
    def filter_remote_friendly(self, queryset, name, value):
        """
        Filter jobs that are remote-friendly (either fully remote or hybrid).
        """
        if value:
            return queryset.filter(
                Q(is_remote=True) | Q(location__icontains='remote') | Q(location__icontains='hybrid')
            )
        return queryset
    
    def filter_posted_days_ago(self, queryset, name, value):
        """Filter jobs posted within the specified number of days."""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=value)
        return queryset.filter(created_at__gte=cutoff_date)
    
    def filter_has_deadline(self, queryset, name, value):
        """Filter jobs based on whether they have an application deadline."""
        if value:
            return queryset.filter(application_deadline__isnull=False)
        else:
            return queryset.filter(application_deadline__isnull=True)
    
    def filter_required_skills(self, queryset, name, value):
        """Filter jobs by required skills (case-insensitive partial match)."""
        return queryset.filter(required_skills__icontains=value)
    
    def filter_preferred_skills(self, queryset, name, value):
        """Filter jobs by preferred skills (case-insensitive partial match)."""
        return queryset.filter(preferred_skills__icontains=value)


class AdvancedJobSearchFilter(BaseFilterBackend):
    """
    Advanced search filter backend for job search functionality.
    Provides full-text search across multiple fields with ranking.
    """
    
    def filter_queryset(self, request, queryset, view):
        search_query = request.query_params.get('search')
        if not search_query:
            return queryset
        
        # Split search query into terms
        search_terms = search_query.split()
        
        # Build Q objects for different search fields with different weights
        title_queries = Q()
        description_queries = Q()
        company_queries = Q()
        location_queries = Q()
        skills_queries = Q()
        
        for term in search_terms:
            # Title search (highest priority)
            title_queries |= Q(title__icontains=term)
            
            # Description search
            description_queries |= Q(description__icontains=term)
            
            # Company name search
            company_queries |= Q(company__name__icontains=term)
            
            # Location search
            location_queries |= Q(location__icontains=term)
            
            # Skills search
            skills_queries |= (
                Q(required_skills__icontains=term) | 
                Q(preferred_skills__icontains=term)
            )
        
        # Combine all search queries
        combined_query = (
            title_queries | description_queries | company_queries | 
            location_queries | skills_queries
        )
        
        return queryset.filter(combined_query).distinct()


class LocationBasedFilter(BaseFilterBackend):
    """
    Location-based filtering with support for radius-based search.
    """
    
    def filter_queryset(self, request, queryset, view):
        # Basic location filtering
        location = request.query_params.get('near_location')
        if not location:
            return queryset
        
        # For now, implement simple text-based location matching
        # In production, this could be enhanced with geocoding and radius search
        location_terms = location.lower().split()
        location_query = Q()
        
        for term in location_terms:
            location_query |= Q(location__icontains=term)
        
        return queryset.filter(location_query)


class CategoryHierarchyFilter(BaseFilterBackend):
    """
    Filter jobs by category hierarchy, including parent and child categories.
    """
    
    def filter_queryset(self, request, queryset, view):
        # Handle both Django and DRF requests
        if hasattr(request, 'query_params'):
            category_id = request.query_params.get('category_hierarchy')
        else:
            category_id = request.GET.get('category_hierarchy')
            
        if not category_id:
            return queryset
        
        try:
            category = Category.objects.get(id=category_id, is_active=True)
            
            # Get all descendant categories
            descendant_categories = [category] + category.get_descendants()
            
            return queryset.filter(categories__in=descendant_categories).distinct()
            
        except Category.DoesNotExist:
            return queryset.none()


class SalaryRangeFilter(BaseFilterBackend):
    """
    Advanced salary range filtering with flexible matching.
    """
    
    def filter_queryset(self, request, queryset, view):
        min_salary = request.query_params.get('min_salary')
        max_salary = request.query_params.get('max_salary')
        
        if not min_salary and not max_salary:
            return queryset
        
        salary_query = Q()
        
        if min_salary:
            try:
                min_val = float(min_salary)
                # Job's salary range overlaps with user's minimum requirement
                salary_query &= (
                    Q(salary_max__gte=min_val) | 
                    (Q(salary_max__isnull=True) & Q(salary_min__gte=min_val)) |
                    (Q(salary_min__isnull=True) & Q(salary_max__isnull=True))
                )
            except ValueError:
                pass
        
        if max_salary:
            try:
                max_val = float(max_salary)
                # Job's salary range overlaps with user's maximum budget
                salary_query &= (
                    Q(salary_min__lte=max_val) | 
                    (Q(salary_min__isnull=True) & Q(salary_max__lte=max_val)) |
                    (Q(salary_min__isnull=True) & Q(salary_max__isnull=True))
                )
            except ValueError:
                pass
        
        return queryset.filter(salary_query) if salary_query else queryset


class RecentJobsFilter(BaseFilterBackend):
    """
    Filter for recently posted jobs with configurable time periods.
    """
    
    def filter_queryset(self, request, queryset, view):
        recent_filter = request.query_params.get('recent')
        if not recent_filter:
            return queryset
        
        from django.utils import timezone
        from datetime import timedelta
        
        # Define time periods
        time_periods = {
            'today': timedelta(days=1),
            'week': timedelta(days=7),
            'month': timedelta(days=30),
            '3months': timedelta(days=90),
        }
        
        if recent_filter in time_periods:
            cutoff_date = timezone.now() - time_periods[recent_filter]
            return queryset.filter(created_at__gte=cutoff_date)
        
        return queryset


class PopularJobsFilter(BaseFilterBackend):
    """
    Filter for popular jobs based on views and applications.
    """
    
    def filter_queryset(self, request, queryset, view):
        popular_filter = request.query_params.get('popular')
        if not popular_filter or popular_filter.lower() != 'true':
            return queryset
        
        # Define popularity criteria (jobs with above-average views or applications)
        from django.db.models import Avg
        
        avg_views = queryset.aggregate(avg_views=Avg('views_count'))['avg_views'] or 0
        avg_applications = queryset.aggregate(avg_apps=Avg('applications_count'))['avg_apps'] or 0
        
        return queryset.filter(
            Q(views_count__gte=avg_views) | Q(applications_count__gte=avg_applications)
        ).distinct()