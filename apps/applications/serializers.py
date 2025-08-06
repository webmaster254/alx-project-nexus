"""
Application serializers for handling API data transformation.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.applications.models import Application, ApplicationStatus, Document
from apps.jobs.models import Job
from apps.jobs.serializers import JobListSerializer
from apps.authentication.serializers import UserSerializer

User = get_user_model()


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Serializer for ApplicationStatus model."""
    
    class Meta:
        model = ApplicationStatus
        fields = ['id', 'name', 'display_name', 'description', 'is_final']
        read_only_fields = ['id']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""
    file_size_display = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField(source='get_file_extension')
    
    class Meta:
        model = Document
        fields = [
            'id', 'document_type', 'title', 'file', 'file_size', 
            'file_size_display', 'file_extension', 'content_type', 
            'description', 'uploaded_at'
        ]
        read_only_fields = ['id', 'file_size', 'content_type', 'uploaded_at']


class ApplicationListSerializer(serializers.ModelSerializer):
    """Optimized serializer for application listings."""
    job = JobListSerializer(read_only=True)
    status = ApplicationStatusSerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    days_since_applied = serializers.ReadOnlyField()
    is_recent = serializers.ReadOnlyField()
    can_withdraw = serializers.ReadOnlyField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'status', 'user_email', 'user_full_name',
            'applied_at', 'updated_at', 'days_since_applied', 
            'is_recent', 'can_withdraw'
        ]
        read_only_fields = ['id', 'applied_at', 'updated_at']


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for application retrieval and updates."""
    job = JobListSerializer(read_only=True)
    status = ApplicationStatusSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    days_since_applied = serializers.ReadOnlyField()
    is_recent = serializers.ReadOnlyField()
    can_withdraw = serializers.ReadOnlyField()
    can_update_status = serializers.ReadOnlyField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'user', 'status', 'cover_letter', 'notes',
            'applied_at', 'updated_at', 'reviewed_at', 'reviewed_by',
            'documents', 'days_since_applied', 'is_recent', 
            'can_withdraw', 'can_update_status'
        ]
        read_only_fields = [
            'id', 'user', 'applied_at', 'updated_at', 'reviewed_at', 
            'reviewed_by', 'documents'
        ]


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new job applications."""
    job_id = serializers.IntegerField(write_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Application
        fields = ['id', 'job_id', 'cover_letter', 'documents']
        read_only_fields = ['id', 'documents']
    
    def validate_job_id(self, value):
        """Validate that the job exists and is accepting applications."""
        try:
            job = Job.objects.get(id=value)
        except Job.DoesNotExist:
            raise serializers.ValidationError("Job not found.")
        
        if not job.can_apply():
            raise serializers.ValidationError(
                "This job is no longer accepting applications."
            )
        
        return value
    
    def validate(self, attrs):
        """Validate application data and check for duplicates."""
        user = self.context['request'].user
        job_id = attrs['job_id']
        
        # Check if user already applied for this job
        if Application.objects.filter(user=user, job_id=job_id).exists():
            raise serializers.ValidationError(
                "You have already applied for this job."
            )
        
        # Check if user is not applying to their own job
        job = Job.objects.get(id=job_id)
        if job.created_by == user:
            raise serializers.ValidationError(
                "You cannot apply to your own job posting."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create a new application."""
        job_id = validated_data.pop('job_id')
        job = Job.objects.get(id=job_id)
        user = self.context['request'].user
        
        # Create application with default status
        application = Application.objects.create(
            user=user,
            job=job,
            **validated_data
        )
        
        # Increment job applications count
        job.increment_applications()
        
        return application


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating application status (admin only)."""
    status_name = serializers.CharField(write_only=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Application
        fields = ['id', 'status_name', 'notes', 'status', 'reviewed_by', 'reviewed_at']
        read_only_fields = ['id', 'status', 'reviewed_by', 'reviewed_at']
    
    def validate_status_name(self, value):
        """Validate that the status exists."""
        try:
            ApplicationStatus.objects.get(name=value)
        except ApplicationStatus.DoesNotExist:
            raise serializers.ValidationError(f"Status '{value}' not found.")
        
        return value
    
    def validate(self, attrs):
        """Validate that the application can be updated."""
        application = self.instance
        
        if not application.can_update_status():
            raise serializers.ValidationError(
                "This application status cannot be updated."
            )
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update application status."""
        status_name = validated_data.pop('status_name')
        notes = validated_data.get('notes', '')
        user = self.context['request'].user
        
        # Get the new status
        new_status = ApplicationStatus.objects.get(name=status_name)
        
        # Update the application
        instance.update_status(
            new_status=new_status,
            reviewed_by=user,
            notes=notes
        )
        
        return instance


class ApplicationWithdrawSerializer(serializers.Serializer):
    """Serializer for withdrawing applications."""
    
    def validate(self, attrs):
        """Validate that the application can be withdrawn."""
        application = self.instance
        
        if not application.can_withdraw():
            raise serializers.ValidationError(
                "This application cannot be withdrawn."
            )
        
        return attrs
    
    def save(self):
        """Withdraw the application."""
        application = self.instance
        application.withdraw()
        return application


class BulkStatusUpdateSerializer(serializers.Serializer):
    """Serializer for bulk status updates (admin only)."""
    application_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of application IDs to update"
    )
    status_name = serializers.CharField(
        max_length=20,
        help_text="New status name (pending, reviewed, accepted, rejected)"
    )
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional notes for the status update"
    )
    
    def validate_status_name(self, value):
        """Validate that the status exists."""
        try:
            ApplicationStatus.objects.get(name=value)
        except ApplicationStatus.DoesNotExist:
            raise serializers.ValidationError(f"Status '{value}' not found.")
        
        return value
    
    def validate_application_ids(self, value):
        """Validate that application IDs exist."""
        if not value:
            raise serializers.ValidationError("At least one application ID is required.")
        
        # Check if applications exist
        existing_count = Application.objects.filter(id__in=value).count()
        if existing_count != len(value):
            raise serializers.ValidationError("Some application IDs do not exist.")
        
        return value


class ApplicationStatusListSerializer(serializers.ModelSerializer):
    """Serializer for listing available application statuses."""
    
    class Meta:
        model = ApplicationStatus
        fields = ['id', 'name', 'display_name', 'description', 'is_final']
        read_only_fields = ['id']