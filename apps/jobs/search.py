"""
Full-text search utilities for job and company models.
Implements PostgreSQL full-text search with ranking and relevance scoring.
"""

from django.db import models
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank, TrigramSimilarity
)
from django.db.models import Q, F, Value, FloatField
from django.db.models.functions import Greatest, Coalesce

from .models import Job, Company


class JobSearchManager:
    """
    Manager class for advanced job search functionality.
    Provides full-text search with ranking and filtering capabilities.
    """
    
    @staticmethod
    def full_text_search(query_text, filters=None, limit=50):
        """
        Perform full-text search on jobs with ranking and relevance scoring.
        
        Args:
            query_text (str): Search query text
            filters (dict): Additional filters to apply
            limit (int): Maximum number of results to return
            
        Returns:
            QuerySet: Ranked search results
        """
        if not query_text or not query_text.strip():
            return Job.objects.none()
        
        # Create search query
        search_query = SearchQuery(query_text, config='english')
        
        # Base queryset with active jobs
        queryset = Job.objects.filter(is_active=True)
        
        # Apply additional filters if provided
        if filters:
            queryset = JobSearchManager._apply_filters(queryset, filters)
        
        # Perform full-text search using search_vector
        queryset = queryset.filter(search_vector=search_query)
        
        # Add ranking and similarity scoring
        queryset = queryset.annotate(
            # Full-text search rank using search_vector
            search_rank=SearchRank(F('search_vector'), search_query),
            
            # Trigram similarity for title
            title_similarity=TrigramSimilarity('title', query_text),
            
            # Trigram similarity for location
            location_similarity=TrigramSimilarity('location', query_text),
            
            # Combined relevance score
            relevance_score=Greatest(
                F('search_rank'),
                F('title_similarity'),
                F('location_similarity'),
                output_field=FloatField()
            )
        ).filter(
            # Filter by minimum relevance threshold
            Q(search_rank__gte=0.1) | 
            Q(title_similarity__gte=0.3) | 
            Q(location_similarity__gte=0.3)
        ).order_by(
            '-relevance_score', '-created_at'
        )[:limit]
        
        return queryset
    
    @staticmethod
    def search_by_title(query_text, filters=None, limit=50):
        """
        Search jobs specifically by title with trigram similarity.
        
        Args:
            query_text (str): Search query text
            filters (dict): Additional filters to apply
            limit (int): Maximum number of results to return
            
        Returns:
            QuerySet: Title-based search results
        """
        if not query_text or not query_text.strip():
            return Job.objects.none()
        
        queryset = Job.objects.filter(is_active=True)
        
        if filters:
            queryset = JobSearchManager._apply_filters(queryset, filters)
        
        # Use trigram similarity for fuzzy title matching
        queryset = queryset.annotate(
            title_similarity=TrigramSimilarity('title', query_text)
        ).filter(
            title_similarity__gte=0.2
        ).order_by(
            '-title_similarity', '-created_at'
        )[:limit]
        
        return queryset
    
    @staticmethod
    def search_by_skills(skills_list, filters=None, limit=50):
        """
        Search jobs by required or preferred skills.
        
        Args:
            skills_list (list): List of skills to search for
            filters (dict): Additional filters to apply
            limit (int): Maximum number of results to return
            
        Returns:
            QuerySet: Skills-based search results
        """
        if not skills_list:
            return Job.objects.none()
        
        queryset = Job.objects.filter(is_active=True)
        
        if filters:
            queryset = JobSearchManager._apply_filters(queryset, filters)
        
        # Build search conditions for skills
        skill_conditions = Q()
        for skill in skills_list:
            skill_conditions |= (
                Q(required_skills__icontains=skill) |
                Q(preferred_skills__icontains=skill)
            )
        
        queryset = queryset.filter(skill_conditions)
        
        # Add relevance scoring based on skill matches
        skill_scores = []
        for skill in skills_list:
            skill_scores.append(
                models.Case(
                    models.When(required_skills__icontains=skill, then=Value(2.0)),
                    models.When(preferred_skills__icontains=skill, then=Value(1.0)),
                    default=Value(0.0),
                    output_field=FloatField()
                )
            )
        
        if skill_scores:
            # Sum all skill match scores
            total_score = skill_scores[0]
            for score in skill_scores[1:]:
                total_score = total_score + score
            
            queryset = queryset.annotate(
                skill_match_score=total_score
            ).order_by(
                '-skill_match_score', '-created_at'
            )[:limit]
        
        return queryset
    
    @staticmethod
    def search_by_location(location_query, filters=None, limit=50):
        """
        Search jobs by location with fuzzy matching.
        
        Args:
            location_query (str): Location search query
            filters (dict): Additional filters to apply
            limit (int): Maximum number of results to return
            
        Returns:
            QuerySet: Location-based search results
        """
        if not location_query or not location_query.strip():
            return Job.objects.none()
        
        queryset = Job.objects.filter(is_active=True)
        
        if filters:
            queryset = JobSearchManager._apply_filters(queryset, filters)
        
        # Use trigram similarity for location matching
        queryset = queryset.annotate(
            location_similarity=TrigramSimilarity('location', location_query)
        ).filter(
            Q(location__icontains=location_query) |
            Q(location_similarity__gte=0.3) |
            Q(is_remote=True)  # Include remote jobs in location searches
        ).order_by(
            '-location_similarity', '-created_at'
        )[:limit]
        
        return queryset
    
    @staticmethod
    def advanced_search(query_text, title=None, location=None, skills=None, 
                       company=None, filters=None, limit=50):
        """
        Perform advanced search combining multiple search criteria.
        
        Args:
            query_text (str): General search query
            title (str): Specific title search
            location (str): Location search
            skills (list): Skills to search for
            company (str): Company name search
            filters (dict): Additional filters
            limit (int): Maximum results
            
        Returns:
            QuerySet: Combined search results
        """
        queryset = Job.objects.filter(is_active=True)
        
        if filters:
            queryset = JobSearchManager._apply_filters(queryset, filters)
        
        search_conditions = Q()
        annotations = {}
        order_fields = []
        
        # General full-text search
        if query_text and query_text.strip():
            search_query = SearchQuery(query_text, config='english')
            search_conditions &= Q(search_vector=search_query)
            annotations['search_rank'] = SearchRank(F('search_vector'), search_query)
            order_fields.append('-search_rank')
        
        # Title-specific search
        if title and title.strip():
            annotations['title_similarity'] = TrigramSimilarity('title', title)
            search_conditions &= Q(title_similarity__gte=0.2)
            order_fields.append('-title_similarity')
        
        # Location-specific search
        if location and location.strip():
            annotations['location_similarity'] = TrigramSimilarity('location', location)
            location_conditions = (
                Q(location__icontains=location) |
                Q(is_remote=True)
            )
            search_conditions &= location_conditions
            order_fields.append('-location_similarity')
        
        # Skills search
        if skills:
            skill_conditions = Q()
            for skill in skills:
                skill_conditions |= (
                    Q(required_skills__icontains=skill) |
                    Q(preferred_skills__icontains=skill)
                )
            search_conditions &= skill_conditions
        
        # Company search
        if company and company.strip():
            annotations['company_similarity'] = TrigramSimilarity('company__name', company)
            search_conditions &= (
                Q(company__name__icontains=company) |
                Q(company_similarity__gte=0.3)
            )
            order_fields.append('-company_similarity')
        
        # Apply search conditions and annotations
        if search_conditions != Q():
            queryset = queryset.filter(search_conditions)
        
        if annotations:
            queryset = queryset.annotate(**annotations)
        
        # Order by relevance and creation date
        if order_fields:
            order_fields.append('-created_at')
            queryset = queryset.order_by(*order_fields)
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset[:limit]
    
    @staticmethod
    def _apply_filters(queryset, filters):
        """
        Apply additional filters to the queryset.
        
        Args:
            queryset: Base queryset
            filters (dict): Filters to apply
            
        Returns:
            QuerySet: Filtered queryset
        """
        if 'industry' in filters and filters['industry']:
            queryset = queryset.filter(industry=filters['industry'])
        
        if 'job_type' in filters and filters['job_type']:
            queryset = queryset.filter(job_type=filters['job_type'])
        
        if 'experience_level' in filters and filters['experience_level']:
            queryset = queryset.filter(experience_level=filters['experience_level'])
        
        if 'salary_min' in filters and filters['salary_min']:
            queryset = queryset.filter(salary_min__gte=filters['salary_min'])
        
        if 'salary_max' in filters and filters['salary_max']:
            queryset = queryset.filter(salary_max__lte=filters['salary_max'])
        
        if 'is_remote' in filters:
            queryset = queryset.filter(is_remote=filters['is_remote'])
        
        if 'is_featured' in filters:
            queryset = queryset.filter(is_featured=filters['is_featured'])
        
        if 'categories' in filters and filters['categories']:
            queryset = queryset.filter(categories__in=filters['categories'])
        
        if 'company' in filters and filters['company']:
            queryset = queryset.filter(company=filters['company'])
        
        return queryset


class CompanySearchManager:
    """
    Manager class for company search functionality.
    """
    
    @staticmethod
    def full_text_search(query_text, limit=20):
        """
        Perform full-text search on companies.
        
        Args:
            query_text (str): Search query text
            limit (int): Maximum number of results
            
        Returns:
            QuerySet: Ranked company search results
        """
        if not query_text or not query_text.strip():
            return Company.objects.none()
        
        search_query = SearchQuery(query_text, config='english')
        
        queryset = Company.objects.filter(
            is_active=True,
            search_vector=search_query
        ).annotate(
            search_rank=SearchRank(F('search_vector'), search_query),
            name_similarity=TrigramSimilarity('name', query_text),
            relevance_score=Greatest(
                F('search_rank'),
                F('name_similarity'),
                output_field=FloatField()
            )
        ).filter(
            Q(search_rank__gte=0.1) | Q(name_similarity__gte=0.3)
        ).order_by(
            '-relevance_score', 'name'
        )[:limit]
        
        return queryset
    
    @staticmethod
    def search_by_name(name_query, limit=20):
        """
        Search companies by name with fuzzy matching.
        
        Args:
            name_query (str): Company name search query
            limit (int): Maximum number of results
            
        Returns:
            QuerySet: Name-based company search results
        """
        if not name_query or not name_query.strip():
            return Company.objects.none()
        
        queryset = Company.objects.filter(
            is_active=True
        ).annotate(
            name_similarity=TrigramSimilarity('name', name_query)
        ).filter(
            Q(name__icontains=name_query) | Q(name_similarity__gte=0.3)
        ).order_by(
            '-name_similarity', 'name'
        )[:limit]
        
        return queryset


# Convenience functions for easy access
def search_jobs(query_text, **kwargs):
    """Convenience function for job full-text search."""
    return JobSearchManager.full_text_search(query_text, **kwargs)


def search_jobs_by_title(query_text, **kwargs):
    """Convenience function for job title search."""
    return JobSearchManager.search_by_title(query_text, **kwargs)


def search_jobs_by_skills(skills_list, **kwargs):
    """Convenience function for job skills search."""
    return JobSearchManager.search_by_skills(skills_list, **kwargs)


def search_jobs_by_location(location_query, **kwargs):
    """Convenience function for job location search."""
    return JobSearchManager.search_by_location(location_query, **kwargs)


def advanced_job_search(**kwargs):
    """Convenience function for advanced job search."""
    return JobSearchManager.advanced_search(**kwargs)


def search_companies(query_text, **kwargs):
    """Convenience function for company search."""
    return CompanySearchManager.full_text_search(query_text, **kwargs)


def search_companies_by_name(name_query, **kwargs):
    """Convenience function for company name search."""
    return CompanySearchManager.search_by_name(name_query, **kwargs)