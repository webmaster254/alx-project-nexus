from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from .models import Job, Company
from apps.categories.models import Industry, JobType, Category

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for Company model with basic information.
    """
    job_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Company
        fields = (
            'id', 'name', 'description', 'website', 'email', 'phone',
            'address', 'logo', 'founded_year', 'employee_count', 'slug',
            'job_count'
        )
        read_only_fields = ('id', 'slug', 'job_count')


class IndustrySerializer(serializers.ModelSerializer):
    """
    Serializer for Industry model.
    """
    job_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Industry
        fields = ('id', 'name', 'description', 'slug', 'job_count')
        read_only_fields = ('id', 'slug', 'job_count')


class JobTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for JobType model.
    """
    job_count = serializers.ReadOnlyField()
    
    class Meta:
        model = JobType
        fields = ('id', 'name', 'code', 'description', 'slug', 'job_count')
        read_only_fields = ('id', 'slug', 'job_count')


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model with hierarchical information.
    """
    job_count = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()
    level = serializers.ReadOnlyField(source='get_level')
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'parent', 
            'job_count', 'full_path', 'level'
        )
        read_only_fields = ('id', 'slug', 'job_count', 'full_path', 'level')


class JobListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for job listing responses.
    Contains essential fields for job listings with minimal nested data.
    """
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_logo = serializers.ImageField(source='company.logo', read_only=True)
    industry_name = serializers.CharField(source='industry.name', read_only=True)
    job_type_name = serializers.CharField(source='job_type.name', read_only=True)
    job_type_code = serializers.CharField(source='job_type.code', read_only=True)
    category_names = serializers.ReadOnlyField()
    salary_display = serializers.ReadOnlyField(source='get_salary_display')
    days_since_posted = serializers.ReadOnlyField()
    is_new = serializers.ReadOnlyField()
    is_urgent = serializers.ReadOnlyField()
    can_apply = serializers.ReadOnlyField()
    required_skills_list = serializers.ReadOnlyField(source='get_required_skills_list')
    
    class Meta:
        model = Job
        fields = (
            'id', 'title', 'summary', 'location', 'is_remote',
            'salary_display', 'salary_type', 'salary_currency',
            'experience_level', 'application_deadline', 'external_url',
            'is_active', 'is_featured', 'views_count', 'applications_count',
            'created_at', 'updated_at', 'company_name', 'company_logo',
            'industry_name', 'job_type_name', 'job_type_code', 'category_names',
            'days_since_posted', 'is_new', 'is_urgent', 'can_apply',
            'required_skills_list'
        )
        read_only_fields = (
            'id', 'views_count', 'applications_count', 'created_at', 'updated_at'
        )


class JobSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for job creation and updates with nested relationships.
    Includes full job details and validation for all fields.
    """
    # Nested serializers for read operations
    company = CompanySerializer(read_only=True)
    industry = IndustrySerializer(read_only=True)
    job_type = JobTypeSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    updated_by = serializers.StringRelatedField(read_only=True)
    
    # Write-only fields for relationships
    company_id = serializers.IntegerField(write_only=True)
    industry_id = serializers.IntegerField(write_only=True)
    job_type_id = serializers.IntegerField(write_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of category IDs to assign to this job"
    )
    
    # Skills as lists for easier frontend handling
    required_skills_list = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        help_text="List of required skills"
    )
    preferred_skills_list = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        help_text="List of preferred skills"
    )
    
    # Read-only computed fields
    salary_display = serializers.ReadOnlyField(source='get_salary_display')
    days_since_posted = serializers.ReadOnlyField()
    is_new = serializers.ReadOnlyField()
    is_urgent = serializers.ReadOnlyField()
    can_apply = serializers.ReadOnlyField()
    category_names = serializers.ReadOnlyField()
    
    class Meta:
        model = Job
        fields = (
            'id', 'title', 'description', 'summary', 'location', 'is_remote',
            'salary_min', 'salary_max', 'salary_type', 'salary_currency',
            'experience_level', 'required_skills', 'preferred_skills',
            'required_skills_list', 'preferred_skills_list',
            'application_deadline', 'external_url', 'is_active', 'is_featured',
            'views_count', 'applications_count', 'created_at', 'updated_at',
            'company', 'company_id', 'industry', 'industry_id',
            'job_type', 'job_type_id', 'categories', 'category_ids',
            'created_by', 'updated_by', 'salary_display', 'days_since_posted',
            'is_new', 'is_urgent', 'can_apply', 'category_names'
        )
        read_only_fields = (
            'id', 'required_skills', 'preferred_skills', 'views_count',
            'applications_count', 'created_at', 'updated_at', 'created_by',
            'updated_by'
        )
        extra_kwargs = {
            'title': {'required': True, 'max_length': 200},
            'description': {'required': True},
            'location': {'required': True, 'max_length': 200},
            'salary_min': {'min_value': Decimal('0')},
            'salary_max': {'min_value': Decimal('0')},
        }
    
    def validate_company_id(self, value):
        """Validate that the company exists and is active."""
        try:
            company = Company.objects.get(id=value)
            if not company.is_active:
                raise serializers.ValidationError("Selected company is not active.")
            return value
        except Company.DoesNotExist:
            raise serializers.ValidationError("Company with this ID does not exist.")
    
    def validate_industry_id(self, value):
        """Validate that the industry exists and is active."""
        try:
            industry = Industry.objects.get(id=value)
            if not industry.is_active:
                raise serializers.ValidationError("Selected industry is not active.")
            return value
        except Industry.DoesNotExist:
            raise serializers.ValidationError("Industry with this ID does not exist.")
    
    def validate_job_type_id(self, value):
        """Validate that the job type exists and is active."""
        try:
            job_type = JobType.objects.get(id=value)
            if not job_type.is_active:
                raise serializers.ValidationError("Selected job type is not active.")
            return value
        except JobType.DoesNotExist:
            raise serializers.ValidationError("Job type with this ID does not exist.")
    
    def validate_category_ids(self, value):
        """Validate that all category IDs exist and are active."""
        if not value:
            return value
        
        # Check for duplicates
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate category IDs are not allowed.")
        
        # Validate each category ID
        existing_categories = Category.objects.filter(
            id__in=value, is_active=True
        ).values_list('id', flat=True)
        
        missing_ids = set(value) - set(existing_categories)
        if missing_ids:
            raise serializers.ValidationError(
                f"Categories with IDs {list(missing_ids)} do not exist or are not active."
            )
        
        return value
    
    def validate_application_deadline(self, value):
        """Validate that application deadline is in the future."""
        if value and value <= timezone.now():
            raise serializers.ValidationError("Application deadline must be in the future.")
        return value
    
    def validate_required_skills_list(self, value):
        """Validate required skills list."""
        if not value:
            return value
        
        # Remove empty strings and duplicates
        skills = [skill.strip() for skill in value if skill.strip()]
        unique_skills = list(dict.fromkeys(skills))  # Preserve order while removing duplicates
        
        if len(unique_skills) > 20:
            raise serializers.ValidationError("Maximum 20 required skills are allowed.")
        
        return unique_skills
    
    def validate_preferred_skills_list(self, value):
        """Validate preferred skills list."""
        if not value:
            return value
        
        # Remove empty strings and duplicates
        skills = [skill.strip() for skill in value if skill.strip()]
        unique_skills = list(dict.fromkeys(skills))  # Preserve order while removing duplicates
        
        if len(unique_skills) > 20:
            raise serializers.ValidationError("Maximum 20 preferred skills are allowed.")
        
        return unique_skills
    
    def validate(self, attrs):
        """Cross-field validation for job data."""
        # Validate salary range
        salary_min = attrs.get('salary_min')
        salary_max = attrs.get('salary_max')
        
        if salary_min and salary_max:
            if salary_min > salary_max:
                raise serializers.ValidationError({
                    'salary_min': 'Minimum salary cannot be greater than maximum salary.'
                })
        
        # Validate that at least one salary value is provided if salary_type is specified
        salary_type = attrs.get('salary_type')
        if salary_type and not salary_min and not salary_max:
            raise serializers.ValidationError({
                'salary_min': 'At least one salary value (min or max) must be provided when salary type is specified.'
            })
        
        # Validate external URL and application deadline combination
        external_url = attrs.get('external_url')
        application_deadline = attrs.get('application_deadline')
        
        if external_url and not application_deadline:
            raise serializers.ValidationError({
                'application_deadline': 'Application deadline is recommended when using external application URL.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create a new job with validated data."""
        # Extract write-only fields
        company_id = validated_data.pop('company_id')
        industry_id = validated_data.pop('industry_id')
        job_type_id = validated_data.pop('job_type_id')
        category_ids = validated_data.pop('category_ids', [])
        required_skills_list = validated_data.pop('required_skills_list', [])
        preferred_skills_list = validated_data.pop('preferred_skills_list', [])
        
        # Set relationships
        validated_data['company_id'] = company_id
        validated_data['industry_id'] = industry_id
        validated_data['job_type_id'] = job_type_id
        
        # Set skills as comma-separated strings
        if required_skills_list:
            validated_data['required_skills'] = ', '.join(required_skills_list)
        if preferred_skills_list:
            validated_data['preferred_skills'] = ', '.join(preferred_skills_list)
        
        # Set created_by from request user
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        
        # Create the job
        job = Job.objects.create(**validated_data)
        
        # Set categories
        if category_ids:
            job.categories.set(category_ids)
        
        return job
    
    def update(self, instance, validated_data):
        """Update an existing job with validated data."""
        # Extract write-only fields
        company_id = validated_data.pop('company_id', None)
        industry_id = validated_data.pop('industry_id', None)
        job_type_id = validated_data.pop('job_type_id', None)
        category_ids = validated_data.pop('category_ids', None)
        required_skills_list = validated_data.pop('required_skills_list', None)
        preferred_skills_list = validated_data.pop('preferred_skills_list', None)
        
        # Update relationships if provided
        if company_id is not None:
            validated_data['company_id'] = company_id
        if industry_id is not None:
            validated_data['industry_id'] = industry_id
        if job_type_id is not None:
            validated_data['job_type_id'] = job_type_id
        
        # Update skills if provided
        if required_skills_list is not None:
            validated_data['required_skills'] = ', '.join(required_skills_list) if required_skills_list else ''
        if preferred_skills_list is not None:
            validated_data['preferred_skills'] = ', '.join(preferred_skills_list) if preferred_skills_list else ''
        
        # Set updated_by from request user
        request = self.context.get('request')
        if request and request.user:
            validated_data['updated_by'] = request.user
        
        # Update the job
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update categories if provided
        if category_ids is not None:
            instance.categories.set(category_ids)
        
        return instance


class JobDetailSerializer(JobSerializer):
    """
    Extended serializer for job detail view with additional computed fields.
    """
    # Additional read-only fields for detailed view
    required_skills_list = serializers.ReadOnlyField(source='get_required_skills_list')
    preferred_skills_list = serializers.ReadOnlyField(source='get_preferred_skills_list')
    is_application_deadline_passed = serializers.ReadOnlyField()
    
    class Meta(JobSerializer.Meta):
        fields = JobSerializer.Meta.fields + (
            'is_application_deadline_passed',
        )