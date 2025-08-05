from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
import json

User = get_user_model()


class UserRegistrationIntegrationTest(APITestCase):
    """Integration tests for user registration functionality."""

    def setUp(self):
        """Set up test data."""
        self.registration_url = reverse('authentication:register')
        self.valid_user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }

    def test_user_registration_success(self):
        """Test successful user registration."""
        response = self.client.post(self.registration_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Check user was created in database
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        
        # Check user profile was created
        user = User.objects.get(email='test@example.com')
        self.assertTrue(hasattr(user, 'profile'))
        
        # Check user data in response
        user_data = response.data['user']
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertEqual(user_data['full_name'], 'Test User')
        self.assertFalse(user_data['is_admin'])

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create a user first
        User.objects.create_user(
            email='test@example.com',
            username='existinguser',
            password='password123'
        )
        
        response = self.client.post(self.registration_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username."""
        # Create a user first
        User.objects.create_user(
            email='existing@example.com',
            username='testuser',
            password='password123'
        )
        
        response = self.client.post(self.registration_url, self.valid_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch."""
        data = self.valid_user_data.copy()
        data['confirm_password'] = 'differentpassword'
        
        response = self.client.post(self.registration_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_user_registration_weak_password(self):
        """Test registration with weak password."""
        data = self.valid_user_data.copy()
        data['password'] = '123'
        data['confirm_password'] = '123'
        
        response = self.client.post(self.registration_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields."""
        # Missing email
        data = self.valid_user_data.copy()
        del data['email']
        
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_invalid_email(self):
        """Test registration with invalid email format."""
        data = self.valid_user_data.copy()
        data['email'] = 'invalid-email'
        
        response = self.client.post(self.registration_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class UserProfileIntegrationTest(APITestCase):
    """Integration tests for user profile management functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)
        
        self.profile_url = reverse('authentication:profile')
        self.user_info_url = reverse('authentication:user_info')
        self.change_password_url = reverse('authentication:change_password')
        
        # Authenticate user
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        """Test retrieving user profile."""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['full_name'], 'Test User')
        self.assertIn('profile', response.data)

    def test_update_user_profile_put(self):
        """Test updating user profile with PUT method."""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+1234567890',
            'bio': 'Updated bio',
            'location': 'New York, NY',
            'skills_list': ['Python', 'Django', 'JavaScript']
        }
        
        response = self.client.put(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check user data was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        
        # Check profile data was updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone_number, '+1234567890')
        self.assertEqual(self.profile.bio, 'Updated bio')
        self.assertEqual(self.profile.location, 'New York, NY')
        self.assertEqual(self.profile.skills, 'Python, Django, JavaScript')

    def test_update_user_profile_patch(self):
        """Test partially updating user profile with PATCH method."""
        update_data = {
            'bio': 'Partially updated bio',
            'location': 'San Francisco, CA'
        }
        
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check only specified fields were updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Partially updated bio')
        self.assertEqual(self.profile.location, 'San Francisco, CA')
        
        # Check other fields remained unchanged
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')  # Should remain unchanged

    def test_update_profile_invalid_phone(self):
        """Test updating profile with invalid phone number."""
        update_data = {
            'phone_number': 'invalid-phone'
        }
        
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)

    def test_get_user_info(self):
        """Test getting current user information."""
        response = self.client.get(self.user_info_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertIn('profile', response.data)

    def test_change_password_success(self):
        """Test successful password change."""
        password_data = {
            'old_password': 'testpass123',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = self.client.post(self.change_password_url, password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check password was actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password."""
        password_data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = self.client.post(self.change_password_url, password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_change_password_mismatch(self):
        """Test password change with password mismatch."""
        password_data = {
            'old_password': 'testpass123',
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        }
        
        response = self.client.post(self.change_password_url, password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_unauthenticated_profile_access(self):
        """Test accessing profile endpoints without authentication."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.get(self.user_info_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(self.change_password_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticationFlowIntegrationTest(APITestCase):
    """Integration tests for complete authentication flow."""

    def setUp(self):
        """Set up test data."""
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')
        self.profile_url = reverse('authentication:profile')
        
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }

    def test_complete_registration_and_login_flow(self):
        """Test complete user registration and login flow."""
        # Step 1: Register user
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        registration_tokens = {
            'access': response.data['access'],
            'refresh': response.data['refresh']
        }
        
        # Step 2: Use registration tokens to access profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {registration_tokens["access"]}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 3: Logout (keep credentials for logout)
        response = self.client.post(self.logout_url, {'refresh': registration_tokens['refresh']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Clear credentials after logout
        self.client.credentials()
        
        # Step 4: Login again
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        new_tokens = {
            'access': response.data['access'],
            'refresh': response.data['refresh']
        }
        
        # Step 5: Use new tokens to access profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_tokens["access"]}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registration_creates_profile_automatically(self):
        """Test that user registration automatically creates a profile."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that profile was created
        user = User.objects.get(email=self.user_data['email'])
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        
        # Check that profile is included in registration response
        self.assertIn('profile', response.data['user'])

    def test_profile_update_after_registration(self):
        """Test updating profile after registration."""
        # Register user
        response = self.client.post(self.register_url, self.user_data, format='json')
        access_token = response.data['access']
        
        # Update profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_update = {
            'bio': 'I am a software developer',
            'location': 'Remote',
            'skills_list': ['Python', 'Django', 'React']
        }
        
        response = self.client.patch(self.profile_url, profile_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify profile was updated
        user = User.objects.get(email=self.user_data['email'])
        profile = user.profile
        self.assertEqual(profile.bio, 'I am a software developer')
        self.assertEqual(profile.location, 'Remote')
        self.assertEqual(profile.skills, 'Python, Django, React')


class AccountManagementIntegrationTest(APITestCase):
    """Integration tests for account management functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user)
        
        self.deactivate_url = reverse('authentication:deactivate_account')
        self.client.force_authenticate(user=self.user)

    def test_account_deactivation(self):
        """Test account deactivation functionality."""
        response = self.client.delete(self.deactivate_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check user is deactivated
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_deactivated_user_cannot_login(self):
        """Test that deactivated user cannot login."""
        # Deactivate user
        self.user.is_active = False
        self.user.save()
        
        # Try to login
        login_url = reverse('authentication:login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        self.client.force_authenticate(user=None)  # Remove authentication
        response = self.client.post(login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)