from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the custom User model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }

    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_email_unique_constraint(self):
        """Test that email must be unique."""
        User.objects.create_user(**self.user_data)
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='test@example.com',
                username='testuser2',
                password='testpass123'
            )

    def test_email_as_username_field(self):
        """Test that email is used as the username field."""
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_required_fields(self):
        """Test required fields configuration."""
        self.assertEqual(User.REQUIRED_FIELDS, ['username'])

    def test_str_representation(self):
        """Test string representation of user."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com')

    def test_get_full_name(self):
        """Test get_full_name method."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), 'Test User')

    def test_get_short_name(self):
        """Test get_short_name method."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), 'Test')

    def test_is_job_seeker_property(self):
        """Test is_job_seeker property."""
        # Regular user should be a job seeker
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_job_seeker)
        
        # Admin user should not be a job seeker
        admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='adminpass123',
            is_admin=True
        )
        self.assertFalse(admin_user.is_job_seeker)

    def test_is_admin_field(self):
        """Test is_admin field functionality."""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_admin)
        
        user.is_admin = True
        user.save()
        user.refresh_from_db()
        self.assertTrue(user.is_admin)


class UserProfileModelTest(TestCase):
    """Test cases for the UserProfile model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.profile_data = {
            'user': self.user,
            'phone_number': '+1234567890',
            'bio': 'Test bio',
            'location': 'Test City, Test State',
            'website': 'https://example.com',
            'linkedin_url': 'https://linkedin.com/in/testuser',
            'github_url': 'https://github.com/testuser',
            'skills': 'Python, Django, JavaScript',
            'experience_years': 5
        }

    def test_create_user_profile(self):
        """Test creating a user profile."""
        profile = UserProfile.objects.create(**self.profile_data)
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.phone_number, '+1234567890')
        self.assertEqual(profile.bio, 'Test bio')
        self.assertEqual(profile.location, 'Test City, Test State')
        self.assertEqual(profile.website, 'https://example.com')
        self.assertEqual(profile.linkedin_url, 'https://linkedin.com/in/testuser')
        self.assertEqual(profile.github_url, 'https://github.com/testuser')
        self.assertEqual(profile.skills, 'Python, Django, JavaScript')
        self.assertEqual(profile.experience_years, 5)
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)

    def test_user_profile_one_to_one_relationship(self):
        """Test one-to-one relationship between User and UserProfile."""
        profile = UserProfile.objects.create(**self.profile_data)
        
        # Test forward relationship
        self.assertEqual(profile.user, self.user)
        
        # Test reverse relationship
        self.assertEqual(self.user.profile, profile)

    def test_user_profile_cascade_delete(self):
        """Test that profile is deleted when user is deleted."""
        profile = UserProfile.objects.create(**self.profile_data)
        profile_id = profile.id
        
        self.user.delete()
        
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=profile_id)

    def test_phone_number_validation(self):
        """Test phone number validation."""
        # Valid phone numbers
        valid_phones = ['+1234567890', '1234567890', '+123456789012345']
        
        for phone in valid_phones:
            profile_data = self.profile_data.copy()
            profile_data['phone_number'] = phone
            profile_data['user'] = User.objects.create_user(
                email=f'test{phone}@example.com',
                username=f'user{phone}',
                password='testpass123'
            )
            profile = UserProfile(**profile_data)
            try:
                profile.full_clean()
            except ValidationError:
                self.fail(f"Valid phone number {phone} failed validation")

        # Invalid phone numbers
        invalid_phones = ['123', 'abc123', '+123456789012345678901']
        
        for phone in invalid_phones:
            profile_data = self.profile_data.copy()
            profile_data['phone_number'] = phone
            profile = UserProfile(**profile_data)
            with self.assertRaises(ValidationError):
                profile.full_clean()

    def test_str_representation(self):
        """Test string representation of user profile."""
        profile = UserProfile.objects.create(**self.profile_data)
        expected_str = f"{self.user.email} - Profile"
        self.assertEqual(str(profile), expected_str)

    def test_get_skills_list(self):
        """Test get_skills_list method."""
        profile = UserProfile.objects.create(**self.profile_data)
        skills_list = profile.get_skills_list()
        expected_skills = ['Python', 'Django', 'JavaScript']
        self.assertEqual(skills_list, expected_skills)

    def test_get_skills_list_empty(self):
        """Test get_skills_list method with empty skills."""
        profile_data = self.profile_data.copy()
        profile_data['skills'] = ''
        profile = UserProfile.objects.create(**profile_data)
        skills_list = profile.get_skills_list()
        self.assertEqual(skills_list, [])

    def test_set_skills_list(self):
        """Test set_skills_list method."""
        profile = UserProfile.objects.create(**self.profile_data)
        new_skills = ['React', 'Node.js', 'PostgreSQL']
        profile.set_skills_list(new_skills)
        self.assertEqual(profile.skills, 'React, Node.js, PostgreSQL')

    def test_set_skills_list_empty(self):
        """Test set_skills_list method with empty list."""
        profile = UserProfile.objects.create(**self.profile_data)
        profile.set_skills_list([])
        self.assertEqual(profile.skills, '')

    def test_optional_fields(self):
        """Test that optional fields can be blank."""
        minimal_profile = UserProfile.objects.create(user=self.user)
        
        self.assertEqual(minimal_profile.phone_number, '')
        self.assertEqual(minimal_profile.bio, '')
        self.assertEqual(minimal_profile.location, '')
        self.assertEqual(minimal_profile.website, '')
        self.assertEqual(minimal_profile.linkedin_url, '')
        self.assertEqual(minimal_profile.github_url, '')
        self.assertEqual(minimal_profile.skills, '')
        self.assertIsNone(minimal_profile.experience_years)
        # FileField returns FieldFile object, not None when blank
        self.assertFalse(minimal_profile.resume)

    def test_experience_years_positive(self):
        """Test that experience_years must be positive."""
        profile_data = self.profile_data.copy()
        profile_data['experience_years'] = -1
        profile = UserProfile(**profile_data)
        
        with self.assertRaises(ValidationError):
            profile.full_clean()
