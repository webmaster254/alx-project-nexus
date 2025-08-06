from rest_framework import serializers
from .models import Category, Industry, JobType


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model with hierarchical information.
    """
    job_count = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()
    level = serializers.ReadOnlyField(source='get_level')
    children = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'parent', 'parent_name',
            'job_count', 'full_path', 'level', 'children', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'job_count', 'full_path', 'level', 'children', 'parent_name', 'created_at', 'updated_at')
        extra_kwargs = {
            'name': {'required': True, 'max_length': 100},
            'description': {'required': False},
        }
    
    def get_children(self, obj):
        """Return serialized children categories."""
        children = obj.children.filter(is_active=True).order_by('name')
        return CategoryListSerializer(children, many=True, context=self.context).data
    
    def validate_parent(self, value):
        """Validate parent category to prevent circular references."""
        if value:
            # Check if parent is active
            if not value.is_active:
                raise serializers.ValidationError("Parent category must be active.")
            
            # For updates, check circular reference
            if hasattr(self, 'instance') and self.instance:
                # Check if setting this parent would create a circular reference
                current = value
                while current:
                    if current == self.instance:
                        raise serializers.ValidationError("Category cannot be its own parent or create circular references.")
                    current = current.parent
                
                # Check depth limit (max 3 levels)
                depth = 1
                current = value
                while current:
                    depth += 1
                    current = current.parent
                    if depth > 3:
                        raise serializers.ValidationError("Category hierarchy cannot exceed 3 levels deep.")
        
        return value


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for category listings.
    """
    job_count = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()
    level = serializers.ReadOnlyField(source='get_level')
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'parent', 'parent_name',
            'job_count', 'full_path', 'level', 'is_active'
        )
        read_only_fields = ('id', 'slug', 'job_count', 'full_path', 'level', 'parent_name')


class CategoryHierarchySerializer(serializers.ModelSerializer):
    """
    Nested serializer for displaying category hierarchy.
    """
    children = serializers.SerializerMethodField()
    job_count = serializers.ReadOnlyField()
    direct_job_count = serializers.SerializerMethodField()
    total_job_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'job_count', 'direct_job_count', 'total_job_count', 'children')
    
    def get_children(self, obj):
        """Return nested children categories."""
        children = obj.children.filter(is_active=True).order_by('name')
        return CategoryHierarchySerializer(children, many=True, context=self.context).data
    
    def get_direct_job_count(self, obj):
        """Return the number of jobs directly in this category."""
        return obj.jobs.filter(is_active=True).count()
    
    def get_total_job_count(self, obj):
        """Return the total number of jobs in this category and all descendants."""
        # This is the same as the job_count property but more explicit
        return obj.job_count


class CategoryWithJobCountSerializer(serializers.ModelSerializer):
    """
    Category serializer with detailed job count information.
    """
    job_count = serializers.ReadOnlyField()
    direct_job_count = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    level = serializers.ReadOnlyField(source='get_level')
    full_path = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'description', 'slug', 'parent', 'parent_name',
            'job_count', 'direct_job_count', 'level', 'full_path', 'is_active'
        )
    
    def get_direct_job_count(self, obj):
        """Return the number of jobs directly in this category."""
        return obj.jobs.filter(is_active=True).count()


class IndustrySerializer(serializers.ModelSerializer):
    """
    Serializer for Industry model.
    """
    job_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Industry
        fields = ('id', 'name', 'description', 'slug', 'job_count', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'job_count', 'created_at', 'updated_at')
        extra_kwargs = {
            'name': {'required': True, 'max_length': 100},
            'description': {'required': False},
        }


class JobTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for JobType model.
    """
    job_count = serializers.ReadOnlyField()
    
    class Meta:
        model = JobType
        fields = ('id', 'name', 'code', 'description', 'slug', 'job_count', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'slug', 'job_count', 'created_at', 'updated_at')
        extra_kwargs = {
            'name': {'required': True, 'max_length': 50},
            'code': {'required': True},
            'description': {'required': False},
        }