from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with basic information.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'is_admin', 'is_active', 'date_joined'
        )
        read_only_fields = ('id', 'date_joined', 'is_active')


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """
    skills_list = serializers.ListField(
        child=serializers.CharField(max_length=50),
        write_only=True,
        required=False,
        help_text="List of skills"
    )
    
    class Meta:
        model = UserProfile
        fields = (
            'phone_number', 'bio', 'location', 'website', 'linkedin_url',
            'github_url', 'resume', 'skills', 'skills_list', 'experience_years'
        )
        extra_kwargs = {
            'skills': {'read_only': True}
        }
    
    def create(self, validated_data):
        skills_list = validated_data.pop('skills_list', None)
        profile = super().create(validated_data)
        
        if skills_list:
            profile.set_skills_list(skills_list)
            profile.save()
        
        return profile
    
    def update(self, instance, validated_data):
        skills_list = validated_data.pop('skills_list', None)
        profile = super().update(instance, validated_data)
        
        if skills_list is not None:
            profile.set_skills_list(skills_list)
            profile.save()
        
        return profile


class UserWithProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with profile information.
    """
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'is_admin', 'is_active', 'date_joined', 'profile'
        )
        read_only_fields = ('id', 'date_joined', 'is_active')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user data in the response.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to the response
        user_serializer = UserWithProfileSerializer(self.user)
        data['user'] = user_serializer.data
        
        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to the token
        token['email'] = user.email
        token['is_admin'] = user.is_admin
        token['full_name'] = user.get_full_name()
        
        return token


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change functionality.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with validation.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        help_text="Confirm your password"
    )
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 
            'password', 'confirm_password'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate that email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Validate that username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_password(self, value):
        """Validate password using Django's password validators."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        """Create a new user with validated data."""
        # Remove confirm_password as it's not needed for user creation
        validated_data.pop('confirm_password', None)
        
        # Create user with hashed password
        user = User.objects.create_user(**validated_data)
        return user