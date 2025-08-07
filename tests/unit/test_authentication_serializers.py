"""
Unit tests for authentication serializers.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.serializers import (
    UserSerializer, UserProfileSerializer, UserWithProfileSerializer,
    CustomTokenObtainPairSerializer, PasswordChangeSerializer,
    UserRegistrationSerializer
)
from tests.base import BaseSerializerTestCase
from tests.factories import UserFactory, UserProfileFactory

User = get_user_model()


class UserSerializerTest(BaseSerializerTestCase):
    """Test cases for UserSerializer."""
    
    def setUp(self):
        self.user = UserFactory()
        self.valid_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = self.assertSerializerValid(UserSerializer, self.valid_data)
        self.assertEqual(serializer.validated_data['email'], 'test@example.com')
        self.assertEqual(serializer.validated_data['username'], 'testuser')
    
    def test_serializer_read_only_fields(self):
        """Test that read-only fields are not included in validated data."""
        data = self.valid_data.copy()
        data.update({
            'id': 999,
            'date_joined': '2023-01-01T00:00:00Z',
            'is_active': False
        })
        
        serializer = self.assertSerializerValid(UserSerializer, data)
        self.assertNotIn('id', serializer.validated_data)
        self.assertNotIn('date_joined', serializer.validated_data)
        self.assertNotIn('is_active', serializer.validated_data)
    
    def test_full_name_field(self):
        """Test full_name computed field."""
        user = UserFactory(first_name='John', last_name='Doe')
        serializer = UserSerializer(user)
        self.assertEqual(serializer.data['full_name'], 'John Doe')
    
    def test_email_validation(self):
        """Test email field validation."""
        # Invalid email
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'invalid-email'
        self.assertSerializerInvalid(UserSerializer, invalid_data, 'email')
    
    def test_username_validation(self):
        """Test username field validation."""
        # Empty username
        invalid_data = self.valid_data.copy()
        invalid_data['username'] = ''
        self.assertSerializerInvalid(UserSerializer, invalid_data, 'username')


class UserProfileSerializerTest(BaseSerializerTestCase):
    """Test cases for UserProfileSerializer."""
    
    def setUp(self):
        self.user = UserFactory()
        self.valid_data = {
            'phone_number': '+1234567890',
            'bio': 'Software developer with 5 years experience',
            'location': 'San Francisco, CA',
            'website': 'https://example.com',
            'linkedin_url': 'https://linkedin.com/in/johndoe',
            'github_url': 'https://github.com/johndoe',
            'skills_list': ['Python', 'JavaScript', 'React'],
            'experience_years': 5
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = self.assertSerializerValid(UserProfileSerializer, self.valid_data)
        self.assertEqual(serializer.validated_data['phone_number'], '+1234567890')
        self.assertEqual(serializer.validated_data['bio'], 'Software developer with 5 years experience')
    
    def test_skills_list_validation(self):
        """Test skills_list field validation."""
        # Valid skills list
        serializer = self.assertSerializerValid(UserProfileSerializer, self.valid_data)
        self.assertEqual(serializer.validated_data['skills_list'], ['Python', 'JavaScript', 'React'])
        
        # Too many skills
        invalid_data = self.valid_data.copy()
        invalid_data['skills_list'] = ['Skill'] * 25  # More than 20
        self.assertSerializerInvalid(UserProfileSerializer, invalid_data, 'skills_list')
        
        # Skill too short
        invalid_data = self.valid_data.copy()
        invalid_data['skills_list'] = ['A']  # Less than 2 characters
        self.assertSerializerInvalid(UserProfileSerializer, invalid_data, 'skills_list')
    
    def test_phone_number_validation(self):
        """Test phone number validation."""
        # Valid phone numbers
        valid_phones = ['+1234567890', '+12345678901234', '']
        for phone in valid_phones:
            data = self.valid_data.copy()
            data['phone_number'] = phone
            self.assertSerializerValid(UserProfileSerializer, data)
        
        # Invalid phone numbers
        invalid_phones = ['123', 'abc123', '12345678901234567890']
        for phone in invalid_phones:
            data = self.valid_data.copy()
            data['phone_number'] = phone
            self.assertSerializerInvalid(UserProfileSerializer, data, 'phone_number')
    
    def test_url_fields_validation(self):
        """Test URL fields validation."""
        url_fields = ['website', 'linkedin_url', 'github_url']
        
        # Valid URLs
        for field in url_fields:
            data = self.valid_data.copy()
            data[field] = 'https://example.com'
            self.assertSerializerValid(UserProfileSerializer, data)
        
        # Invalid URLs
        for field in url_fields:
            data = self.valid_data.copy()
            data[field] = 'not-a-url'
            self.assertSerializerInvalid(UserProfileSerializer, data, field)
    
    def test_create_with_skills_list(self):
        """Test create method with skills_list."""
        user = UserFactory()
        data = self.valid_data.copy()
        
        serializer = UserProfileSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        profile = serializer.save(user=user)
        self.assertEqual(profile.skills, 'Python, JavaScript, React')
        self.assertEqual(profile.get_skills_list(), ['Python', 'JavaScript', 'React'])
    
    def test_update_with_skills_list(self):
        """Test update method with skills_list."""
        profile = UserProfileFactory(skills='Old, Skills')
        data = {'skills_list': ['New', 'Skills']}
        
        serializer = UserProfileSerializer(profile, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_profile = serializer.save()
        self.assertEqual(updated_profile.skills, 'New, Skills')


class UserWithProfileSerializerTest(BaseSerializerTestCase):
    """Test cases for UserWithProfileSerializer."""
    
    def test_serializer_includes_profile(self):
        """Test that serializer includes profile data."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        
        serializer = UserWithProfileSerializer(user)
        self.assertIn('profile', serializer.data)
        self.assertEqual(serializer.data['profile']['bio'], profile.bio)
    
    def test_serializer_with_no_profile(self):
        """Test serializer with user that has no profile."""
        user = UserFactory()
        
        serializer = UserWithProfileSerializer(user)
        self.assertIn('profile', serializer.data)
        self.assertIsNone(serializer.data['profile'])


class CustomTokenObtainPairSerializerTest(BaseSerializerTestCase):
    """Test cases for CustomTokenObtainPairSerializer."""
    
    def setUp(self):
        self.user = UserFactory(email='test@example.com', password='testpass123')
        self.user.set_password('testpass123')
        self.user.save()
        
        self.valid_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    def test_validate_includes_user_data(self):
        """Test that validate method includes user data."""
        serializer = CustomTokenObtainPairSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        validated_data = serializer.validated_data
        self.assertIn('user', validated_data)
        self.assertEqual(validated_data['user']['email'], 'test@example.com')
    
    def test_get_token_includes_custom_claims(self):
        """Test that get_token includes custom claims."""
        token = CustomTokenObtainPairSerializer.get_token(self.user)
        
        self.assertEqual(token['email'], self.user.email)
        self.assertEqual(token['is_admin'], self.user.is_admin)
        self.assertEqual(token['full_name'], self.user.get_full_name())


class PasswordChangeSerializerTest(BaseSerializerTestCase):
    """Test cases for PasswordChangeSerializer."""
    
    def setUp(self):
        self.user = UserFactory()
        self.user.set_password('oldpass123')
        self.user.save()
        
        self.factory = APIRequestFactory()
        self.request = self.factory.post('/')
        self.request.user = self.user
        
        self.valid_data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        context = {'request': self.request}
        serializer = self.assertSerializerValid(
            PasswordChangeSerializer, self.valid_data, context
        )
    
    def test_old_password_validation(self):
        """Test old password validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['old_password'] = 'wrongpass'
        
        context = {'request': self.request}
        self.assertSerializerInvalid(
            PasswordChangeSerializer, invalid_data, 'old_password', context
        )
    
    def test_password_confirmation_validation(self):
        """Test password confirmation validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['confirm_password'] = 'differentpass'
        
        context = {'request': self.request}
        self.assertSerializerInvalid(
            PasswordChangeSerializer, invalid_data, context=context
        )
    
    def test_new_password_length_validation(self):
        """Test new password length validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['new_password'] = '123'  # Too short
        invalid_data['confirm_password'] = '123'
        
        context = {'request': self.request}
        self.assertSerializerInvalid(
            PasswordChangeSerializer, invalid_data, 'new_password', context
        )


class UserRegistrationSerializerTest(BaseSerializerTestCase):
    """Test cases for UserRegistrationSerializer."""
    
    def setUp(self):
        self.valid_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = self.assertSerializerValid(UserRegistrationSerializer, self.valid_data)
        self.assertEqual(serializer.validated_data['email'], 'newuser@example.com')
    
    def test_email_uniqueness_validation(self):
        """Test email uniqueness validation."""
        # Create existing user
        UserFactory(email='existing@example.com')
        
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'existing@example.com'
        
        self.assertSerializerInvalid(UserRegistrationSerializer, invalid_data, 'email')
    
    def test_username_uniqueness_validation(self):
        """Test username uniqueness validation."""
        # Create existing user
        UserFactory(username='existinguser')
        
        invalid_data = self.valid_data.copy()
        invalid_data['username'] = 'existinguser'
        
        self.assertSerializerInvalid(UserRegistrationSerializer, invalid_data, 'username')
    
    def test_password_confirmation_validation(self):
        """Test password confirmation validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['confirm_password'] = 'differentpass'
        
        self.assertSerializerInvalid(UserRegistrationSerializer, invalid_data)
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Weak password
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = '123'
        invalid_data['confirm_password'] = '123'
        
        self.assertSerializerInvalid(UserRegistrationSerializer, invalid_data, 'password')
    
    def test_create_user(self):
        """Test user creation."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        
        # Check user was created correctly
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertTrue(user.check_password('securepass123'))
        
        # Check confirm_password was not saved
        self.assertFalse(hasattr(user, 'confirm_password'))
    
    def test_required_fields(self):
        """Test required fields validation."""
        required_fields = ['email', 'username', 'first_name', 'last_name', 'password']
        
        for field in required_fields:
            invalid_data = self.valid_data.copy()
            invalid_data.pop(field)
            
            self.assertSerializerInvalid(UserRegistrationSerializer, invalid_data, field)
    
    def test_email_case_normalization(self):
        """Test that email is normalized to lowercase."""
        data = self.valid_data.copy()
        data['email'] = 'TEST@EXAMPLE.COM'
        
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.email, 'test@example.com')