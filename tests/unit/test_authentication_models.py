"""
Unit tests for authentication models.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.authentication.models import User, UserProfile
from tests.base import BaseModelTestCase
from tests.factories import UserFactory, UserProfileFactory

User = get_user_model()


class UserModelTest(BaseModelTestCase):
    """Test cases for User model."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user = UserFactory()
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
    
    def test_user_str_representation(self):
        """Test user string representation."""
        user = UserFactory(email='test@example.com')
        self.assertEqual(str(user), 'test@example.com')
    
    def test_email_as_username_field(self):
        """Test that email is used as username field."""
        self.assertEqual(User.USERNAME_FIELD, 'email')
        self.assertIn('username', User.REQUIRED_FIELDS)
    
    def test_email_uniqueness(self):
        """Test that email must be unique."""
        email = 'test@example.com'
        UserFactory(email=email)
        
        with self.assertRaises(IntegrityError):
            UserFactory(email=email)
    
    def test_username_uniqueness(self):
        """Test that username must be unique."""
        username = 'testuser'
        UserFactory(username=username)
        
        with self.assertRaises(IntegrityError):
            UserFactory(username=username)
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        user = UserFactory(first_name='John', last_name='Doe')
        self.assertEqual(user.get_full_name(), 'John Doe')
        
        # Test with empty names
        user_empty = UserFactory(first_name='', last_name='')
        self.assertEqual(user_empty.get_full_name(), '')
        
        # Test with only first name
        user_first_only = UserFactory(first_name='John', last_name='')
        self.assertEqual(user_first_only.get_full_name(), 'John')
    
    def test_get_short_name(self):
        """Test get_short_name method."""
        user = UserFactory(first_name='John')
        self.assertEqual(user.get_short_name(), 'John')
    
    def test_is_job_seeker_property(self):
        """Test is_job_seeker property."""
        regular_user = UserFactory(is_admin=False)
        admin_user = UserFactory(is_admin=True)
        
        self.assertTrue(regular_user.is_job_seeker)
        self.assertFalse(admin_user.is_job_seeker)
    
    def test_admin_user_creation(self):
        """Test admin user creation."""
        admin_user = UserFactory(is_admin=True, is_staff=True, is_superuser=True)
        self.assertTrue(admin_user.is_admin)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertFalse(admin_user.is_job_seeker)
    
    def test_user_meta_options(self):
        """Test user model meta options."""
        self.assertEqual(User._meta.db_table, 'auth_user')
        self.assertEqual(User._meta.verbose_name, 'User')
        self.assertEqual(User._meta.verbose_name_plural, 'Users')


class UserProfileModelTest(BaseModelTestCase):
    """Test cases for UserProfile model."""
    
    def test_user_profile_creation(self):
        """Test basic user profile creation."""
        profile = UserProfileFactory()
        self.assertIsInstance(profile, UserProfile)
        self.assertIsNotNone(profile.user)
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
    
    def test_user_profile_str_representation(self):
        """Test user profile string representation."""
        user = UserFactory(email='test@example.com')
        profile = UserProfileFactory(user=user)
        expected_str = 'test@example.com - Profile'
        self.assertEqual(str(profile), expected_str)
    
    def test_one_to_one_relationship_with_user(self):
        """Test one-to-one relationship with User."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        
        # Test forward relationship
        self.assertEqual(profile.user, user)
        
        # Test reverse relationship
        self.assertEqual(user.profile, profile)
    
    def test_phone_number_validation(self):
        """Test phone number validation."""
        # Valid phone numbers
        valid_phones = ['+1234567890', '+12345678901234', '1234567890']
        for phone in valid_phones:
            profile = UserProfileFactory.build(phone_number=phone)
            self.assertModelValid(profile)
        
        # Invalid phone numbers
        invalid_phones = ['123', '12345678901234567890', 'abc123', '']
        for phone in invalid_phones:
            if phone:  # Skip empty string as it's allowed
                profile = UserProfileFactory.build(phone_number=phone)
                self.assertModelInvalid(profile, 'phone_number')
    
    def test_bio_max_length(self):
        """Test bio field max length validation."""
        # Valid bio
        valid_bio = 'x' * 500
        profile = UserProfileFactory.build(bio=valid_bio)
        self.assertModelValid(profile)
        
        # Invalid bio (too long)
        invalid_bio = 'x' * 501
        profile = UserProfileFactory.build(bio=invalid_bio)
        self.assertModelInvalid(profile, 'bio')
    
    def test_location_max_length(self):
        """Test location field max length validation."""
        # Valid location
        valid_location = 'x' * 100
        profile = UserProfileFactory.build(location=valid_location)
        self.assertModelValid(profile)
        
        # Invalid location (too long)
        invalid_location = 'x' * 101
        profile = UserProfileFactory.build(location=invalid_location)
        self.assertModelInvalid(profile, 'location')
    
    def test_experience_years_validation(self):
        """Test experience years validation."""
        # Valid experience years
        valid_years = [0, 5, 20, 50]
        for years in valid_years:
            profile = UserProfileFactory.build(experience_years=years)
            self.assertModelValid(profile)
        
        # Invalid experience years (negative)
        profile = UserProfileFactory.build(experience_years=-1)
        self.assertModelInvalid(profile, 'experience_years')
    
    def test_get_skills_list_method(self):
        """Test get_skills_list method."""
        # Test with skills
        profile = UserProfileFactory(skills='Python, JavaScript, React')
        expected_skills = ['Python', 'JavaScript', 'React']
        self.assertEqual(profile.get_skills_list(), expected_skills)
        
        # Test with empty skills
        profile_empty = UserProfileFactory(skills='')
        self.assertEqual(profile_empty.get_skills_list(), [])
        
        # Test with None skills
        profile_none = UserProfileFactory(skills=None)
        self.assertEqual(profile_none.get_skills_list(), [])
        
        # Test with skills containing extra spaces
        profile_spaces = UserProfileFactory(skills='Python,  JavaScript , React  ')
        expected_skills_clean = ['Python', 'JavaScript', 'React']
        self.assertEqual(profile_spaces.get_skills_list(), expected_skills_clean)
    
    def test_set_skills_list_method(self):
        """Test set_skills_list method."""
        profile = UserProfileFactory()
        
        # Test setting skills list
        skills_list = ['Python', 'JavaScript', 'React']
        profile.set_skills_list(skills_list)
        self.assertEqual(profile.skills, 'Python, JavaScript, React')
        
        # Test setting empty list
        profile.set_skills_list([])
        self.assertEqual(profile.skills, '')
        
        # Test setting None
        profile.set_skills_list(None)
        self.assertEqual(profile.skills, '')
    
    def test_url_fields_validation(self):
        """Test URL fields validation."""
        # Valid URLs
        valid_urls = [
            'https://example.com',
            'http://example.com',
            'https://subdomain.example.com/path',
            ''  # Empty is allowed
        ]
        
        url_fields = ['website', 'linkedin_url', 'github_url']
        
        for url in valid_urls:
            for field in url_fields:
                profile = UserProfileFactory.build(**{field: url})
                self.assertModelValid(profile)
        
        # Invalid URLs
        invalid_urls = ['not-a-url', 'ftp://example.com', 'javascript:alert(1)']
        
        for url in invalid_urls:
            for field in url_fields:
                profile = UserProfileFactory.build(**{field: url})
                self.assertModelInvalid(profile, field)
    
    def test_resume_file_field(self):
        """Test resume file field."""
        profile = UserProfileFactory()
        
        # Test that resume field exists and can be None
        self.assertIsNone(profile.resume)
        
        # Test file upload (would need actual file handling in integration tests)
        self.assertTrue(hasattr(profile, 'resume'))
    
    def test_profile_meta_options(self):
        """Test user profile model meta options."""
        self.assertEqual(UserProfile._meta.db_table, 'user_profile')
        self.assertEqual(UserProfile._meta.verbose_name, 'User Profile')
        self.assertEqual(UserProfile._meta.verbose_name_plural, 'User Profiles')
    
    def test_cascade_delete_with_user(self):
        """Test that profile is deleted when user is deleted."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        profile_id = profile.id
        
        # Delete user
        user.delete()
        
        # Profile should be deleted too
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=profile_id)