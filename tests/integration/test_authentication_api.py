"""
Integration tests for authentication API endpoints.
Tests all authentication flows including registration, login, logout, and profile management.
"""
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from tests.base import BaseAPIEndpointTestCase
from tests.factories import UserFactory, UserProfileFactory

User = get_user_model()


class AuthenticationAPITestCase(BaseAPIEndpointTestCase):
    """Test authentication API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')
        self.profile_url = reverse('authentication:profile')
        self.user_info_url = reverse('authentication:user_info')
        self.change_password_url = reverse('authentication:change_password')
        self.token_refresh_url = reverse('authentication:token_refresh')
        self.token_verify_url = reverse('authentication:token_verify')
        self.verify_token_url = reverse('authentication:verify_token')
        self.deactivate_url = reverse('authentication:deactivate_account')
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertResponseHasKeys(response, ['user', 'access', 'refresh'])
        
        # Verify user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertFalse(user.is_admin)
    
    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username."""
        existing_user = UserFactory(username='testuser')
        
        data = {
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertValidationError(response, 'username')
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        existing_user = UserFactory(email='test@example.com')
        
        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertValidationError(response, 'email')
    
    def test_user_registration_invalid_data(self):
        """Test registration with invalid data."""
        # Missing required fields
        data = {
            'username': 'newuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertValidationError(response, 'email')
    
    def test_user_registration_weak_password(self):
        """Test registration with weak password."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',
            'confirm_password': '123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(self.register_url, data)
        
        self.assertValidationError(response, 'password')
    
    def test_user_login_success(self):
        """Test successful user login."""
        user = UserFactory(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        user.save()
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertResponseHasKeys(response, ['user', 'access', 'refresh'])
        
        # Verify user data in response
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['email'], 'test@example.com')
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        user = UserFactory(email='test@example.com')
        user.set_password('testpass123')
        user.save()
        
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertResponseStatus(response, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_login_nonexistent_user(self):
        """Test login with nonexistent user."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertResponseStatus(response, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_login_inactive_user(self):
        """Test login with inactive user."""
        user = UserFactory(email='test@example.com', is_active=False)
        user.set_password('testpass123')
        user.save()
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertResponseStatus(response, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_logout_success(self):
        """Test successful user logout."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        self.authenticate_user(user)
        
        data = {
            'refresh': str(refresh)
        }
        
        response = self.client.post(self.logout_url, data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
    
    def test_user_logout_unauthenticated(self):
        """Test logout without authentication."""
        response = self.client.post(self.logout_url, {})
        
        self.assertPermissionDenied(response)
    
    def test_user_logout_invalid_refresh_token(self):
        """Test logout with invalid refresh token."""
        self.authenticate_user()
        
        data = {
            'refresh': 'invalid_token'
        }
        
        response = self.client.post(self.logout_url, data)
        
        self.assertResponseStatus(response, status.HTTP_400_BAD_REQUEST)
    
    def test_get_user_profile_success(self):
        """Test getting user profile."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        self.authenticate_user(user)
        
        response = self.client.get(self.profile_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertResponseHasKeys(response, [
            'phone_number', 'bio', 'location', 'website',
            'linkedin_url', 'github_url', 'skills', 'experience_years'
        ])
    
    def test_get_user_profile_unauthenticated(self):
        """Test getting profile without authentication."""
        response = self.client.get(self.profile_url)
        
        self.assertPermissionDenied(response)
    
    def test_update_user_profile_success(self):
        """Test updating user profile."""
        user = UserFactory()
        profile = UserProfileFactory(user=user)
        self.authenticate_user(user)
        
        data = {
            'phone_number': '+1-555-999-8888',
            'bio': 'Updated bio',
            'location': 'New York, NY',
            'website': 'https://newwebsite.com',
            'skills': 'Python, Django, React, PostgreSQL',
            'experience_years': 5
        }
        
        response = self.client.put(self.profile_url, data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Verify profile was updated
        profile.refresh_from_db()
        self.assertEqual(profile.phone_number, '+1-555-999-8888')
        self.assertEqual(profile.bio, 'Updated bio')
        self.assertEqual(profile.location, 'New York, NY')
        self.assertEqual(profile.experience_years, 5)
    
    def test_update_user_profile_partial(self):
        """Test partial update of user profile."""
        user = UserFactory()
        profile = UserProfileFactory(user=user, bio='Original bio')
        self.authenticate_user(user)
        
        data = {
            'bio': 'Updated bio only'
        }
        
        response = self.client.patch(self.profile_url, data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Verify only bio was updated
        profile.refresh_from_db()
        self.assertEqual(profile.bio, 'Updated bio only')
    
    def test_get_user_info_success(self):
        """Test getting user information."""
        user = UserFactory(first_name='John', last_name='Doe')
        self.authenticate_user(user)
        
        response = self.client.get(self.user_info_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertResponseHasKeys(response, [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_admin', 'created_at', 'updated_at'
        ])
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Doe')
    
    def test_get_user_info_unauthenticated(self):
        """Test getting user info without authentication."""
        response = self.client.get(self.user_info_url)
        
        self.assertPermissionDenied(response)
    
    def test_change_password_success(self):
        """Test successful password change."""
        user = UserFactory()
        user.set_password('oldpassword123')
        user.save()
        self.authenticate_user(user)
        
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123'
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Verify password was changed
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword123'))
        self.assertFalse(user.check_password('oldpassword123'))
    
    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password."""
        user = UserFactory()
        user.set_password('oldpassword123')
        user.save()
        self.authenticate_user(user)
        
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertValidationError(response, 'old_password')
    
    def test_change_password_weak_new_password(self):
        """Test password change with weak new password."""
        user = UserFactory()
        user.set_password('oldpassword123')
        user.save()
        self.authenticate_user(user)
        
        data = {
            'old_password': 'oldpassword123',
            'new_password': '123'
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertValidationError(response, 'new_password')
    
    def test_change_password_unauthenticated(self):
        """Test password change without authentication."""
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123'
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertPermissionDenied(response)
    
    def test_token_refresh_success(self):
        """Test successful token refresh."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        
        data = {
            'refresh': str(refresh)
        }
        
        response = self.client.post(self.token_refresh_url, data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertResponseHasKeys(response, ['access'])
    
    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid token."""
        data = {
            'refresh': 'invalid_token'
        }
        
        response = self.client.post(self.token_refresh_url, data)
        
        self.assertResponseStatus(response, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_verify_success(self):
        """Test successful token verification."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        data = {
            'token': access_token
        }
        
        response = self.client.post(self.token_verify_url, data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
    
    def test_token_verify_invalid_token(self):
        """Test token verification with invalid token."""
        data = {
            'token': 'invalid_token'
        }
        
        response = self.client.post(self.token_verify_url, data)
        
        self.assertResponseStatus(response, status.HTTP_401_UNAUTHORIZED)
    
    def test_verify_token_endpoint_success(self):
        """Test custom verify token endpoint."""
        user = UserFactory()
        self.authenticate_user(user)
        
        response = self.client.get(self.verify_token_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertResponseHasKeys(response, ['user'])
    
    def test_verify_token_endpoint_unauthenticated(self):
        """Test custom verify token endpoint without authentication."""
        response = self.client.get(self.verify_token_url)
        
        self.assertPermissionDenied(response)
    
    def test_deactivate_account_success(self):
        """Test successful account deactivation."""
        user = UserFactory(is_active=True)
        self.authenticate_user(user)
        
        response = self.client.post(self.deactivate_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Verify user was deactivated
        user.refresh_from_db()
        self.assertFalse(user.is_active)
    
    def test_deactivate_account_unauthenticated(self):
        """Test account deactivation without authentication."""
        response = self.client.post(self.deactivate_url)
        
        self.assertPermissionDenied(response)
    
    def test_admin_user_login_has_admin_flag(self):
        """Test that admin users have is_admin flag set in response."""
        admin_user = UserFactory(is_admin=True, is_staff=True)
        admin_user.set_password('testpass123')
        admin_user.save()
        
        data = {
            'email': admin_user.email,
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertTrue(response.data['user']['is_admin'])
    
    def test_regular_user_login_no_admin_flag(self):
        """Test that regular users don't have is_admin flag set."""
        user = UserFactory(is_admin=False)
        user.set_password('testpass123')
        user.save()
        
        data = {
            'email': user.email,
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertFalse(response.data['user']['is_admin'])


class AuthenticationFlowTestCase(BaseAPIEndpointTestCase):
    """Test complete authentication flows."""
    
    def test_complete_registration_and_login_flow(self):
        """Test complete user registration and login flow."""
        # Step 1: Register user
        register_data = {
            'username': 'flowuser',
            'email': 'flowuser@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Flow',
            'last_name': 'User'
        }
        
        register_response = self.client.post(
            reverse('authentication:register'), 
            register_data
        )
        
        self.assertResponseStatus(register_response, status.HTTP_201_CREATED)
        access_token = register_response.data['access']
        refresh_token = register_response.data['refresh']
        
        # Step 2: Use access token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get(reverse('authentication:profile'))
        self.assertResponseStatus(profile_response, status.HTTP_200_OK)
        
        # Step 3: Refresh token
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post(
            reverse('authentication:token_refresh'),
            refresh_data
        )
        
        self.assertResponseStatus(refresh_response, status.HTTP_200_OK)
        new_access_token = refresh_response.data['access']
        
        # Step 4: Use new access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        user_info_response = self.client.get(reverse('authentication:user_info'))
        self.assertResponseStatus(user_info_response, status.HTTP_200_OK)
        
        # Step 5: Logout
        logout_data = {'refresh': refresh_token}
        logout_response = self.client.post(
            reverse('authentication:logout'),
            logout_data
        )
        
        self.assertResponseStatus(logout_response, status.HTTP_200_OK)
    
    def test_profile_creation_and_update_flow(self):
        """Test profile creation and update flow."""
        # Step 1: Register user (creates profile automatically)
        register_data = {
            'username': 'profileuser',
            'email': 'profileuser@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Profile',
            'last_name': 'User'
        }
        
        register_response = self.client.post(
            reverse('authentication:register'),
            register_data
        )
        
        self.assertResponseStatus(register_response, status.HTTP_201_CREATED)
        access_token = register_response.data['access']
        
        # Step 2: Get initial profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get(reverse('authentication:profile'))
        self.assertResponseStatus(profile_response, status.HTTP_200_OK)
        
        # Step 3: Update profile
        profile_data = {
            'phone_number': '+1-555-123-4567',
            'bio': 'I am a software developer',
            'location': 'San Francisco, CA',
            'website': 'https://mywebsite.com',
            'skills': 'Python, Django, JavaScript, React',
            'experience_years': 3
        }
        
        update_response = self.client.put(
            reverse('authentication:profile'),
            profile_data
        )
        
        self.assertResponseStatus(update_response, status.HTTP_200_OK)
        
        # Step 4: Verify profile was updated
        updated_profile_response = self.client.get(reverse('authentication:profile'))
        self.assertResponseStatus(updated_profile_response, status.HTTP_200_OK)
        
        profile_data_response = updated_profile_response.data
        self.assertEqual(profile_data_response['phone_number'], '+1-555-123-4567')
        self.assertEqual(profile_data_response['bio'], 'I am a software developer')
        self.assertEqual(profile_data_response['experience_years'], 3)
    
    def test_password_change_flow(self):
        """Test password change flow."""
        # Step 1: Create user with known password
        user = UserFactory(email='passworduser@example.com')
        user.set_password('oldpassword123')
        user.save()
        
        # Step 2: Login with old password
        login_data = {
            'email': 'passworduser@example.com',
            'password': 'oldpassword123'
        }
        
        login_response = self.client.post(
            reverse('authentication:login'),
            login_data
        )
        
        self.assertResponseStatus(login_response, status.HTTP_200_OK)
        access_token = login_response.data['access']
        
        # Step 3: Change password
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        change_password_data = {
            'old_password': 'oldpassword123',
            'new_password': 'newpassword123'
        }
        
        change_response = self.client.post(
            reverse('authentication:change_password'),
            change_password_data
        )
        
        self.assertResponseStatus(change_response, status.HTTP_200_OK)
        
        # Step 4: Logout
        self.client.credentials()
        
        # Step 5: Try to login with old password (should fail)
        old_login_response = self.client.post(
            reverse('authentication:login'),
            login_data
        )
        
        self.assertResponseStatus(old_login_response, status.HTTP_401_UNAUTHORIZED)
        
        # Step 6: Login with new password (should succeed)
        new_login_data = {
            'email': 'passworduser@example.com',
            'password': 'newpassword123'
        }
        
        new_login_response = self.client.post(
            reverse('authentication:login'),
            new_login_data
        )
        
        self.assertResponseStatus(new_login_response, status.HTTP_200_OK)