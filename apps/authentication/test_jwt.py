from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import json

User = get_user_model()


class JWTAuthenticationTest(APITestCase):
    """Test cases for JWT authentication functionality."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        
        self.admin_data = {
            'email': 'admin@example.com',
            'username': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
            'password': 'adminpass123',
            'is_admin': True
        }
        self.admin_user = User.objects.create_user(**self.admin_data)

    def test_token_obtain_pair_success(self):
        """Test successful JWT token generation."""
        url = reverse('authentication:token_obtain_pair')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Check user data in response
        user_data = response.data['user']
        self.assertEqual(user_data['email'], self.user.email)
        self.assertEqual(user_data['full_name'], 'Test User')
        self.assertFalse(user_data['is_admin'])

    def test_token_obtain_pair_admin_user(self):
        """Test JWT token generation for admin user."""
        url = reverse('authentication:token_obtain_pair')
        data = {
            'email': self.admin_data['email'],
            'password': self.admin_data['password']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data['user']
        self.assertTrue(user_data['is_admin'])

    def test_token_obtain_pair_invalid_credentials(self):
        """Test JWT token generation with invalid credentials."""
        url = reverse('authentication:token_obtain_pair')
        data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_obtain_pair_missing_fields(self):
        """Test JWT token generation with missing fields."""
        url = reverse('authentication:token_obtain_pair')
        
        # Missing password
        data = {'email': self.user_data['email']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing email
        data = {'password': self.user_data['password']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_refresh_success(self):
        """Test successful JWT token refresh."""
        # First get tokens
        refresh = RefreshToken.for_user(self.user)
        
        url = reverse('authentication:token_refresh')
        data = {'refresh': str(refresh)}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid_token(self):
        """Test JWT token refresh with invalid token."""
        url = reverse('authentication:token_refresh')
        data = {'refresh': 'invalid_token'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_verify_success(self):
        """Test successful JWT token verification."""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        url = reverse('authentication:token_verify')
        data = {'token': access_token}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_verify_invalid_token(self):
        """Test JWT token verification with invalid token."""
        url = reverse('authentication:token_verify')
        data = {'token': 'invalid_token'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_view_success(self):
        """Test alternative login view success."""
        url = reverse('authentication:login')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_view_invalid_credentials(self):
        """Test alternative login view with invalid credentials."""
        url = reverse('authentication:login')
        data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_view_inactive_user(self):
        """Test login with inactive user."""
        self.user.is_active = False
        self.user.save()
        
        url = reverse('authentication:login')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_view_missing_fields(self):
        """Test login view with missing fields."""
        url = reverse('authentication:login')
        
        # Missing password
        data = {'email': self.user_data['email']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing email
        data = {'password': self.user_data['password']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_view_success(self):
        """Test successful logout with token blacklisting."""
        refresh = RefreshToken.for_user(self.user)
        
        url = reverse('authentication:logout')
        data = {'refresh': str(refresh)}
        
        # Authenticate the request
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_logout_view_missing_token(self):
        """Test logout view with missing refresh token."""
        url = reverse('authentication:logout')
        data = {}
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_logout_view_invalid_token(self):
        """Test logout view with invalid refresh token."""
        url = reverse('authentication:logout')
        data = {'refresh': 'invalid_token'}
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_verify_token_view_success(self):
        """Test custom token verification view success."""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        url = reverse('authentication:verify_token')
        data = {'token': access_token}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])

    def test_verify_token_view_invalid_token(self):
        """Test custom token verification view with invalid token."""
        url = reverse('authentication:verify_token')
        data = {'token': 'invalid_token'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['valid'])

    def test_verify_token_view_missing_token(self):
        """Test custom token verification view with missing token."""
        url = reverse('authentication:verify_token')
        data = {}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_authenticated_request_with_jwt(self):
        """Test making authenticated requests with JWT token."""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        # Set the authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Make a request to a protected endpoint (we'll use token verify as example)
        url = reverse('authentication:token_verify')
        data = {'token': access_token}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_custom_token_claims(self):
        """Test that custom claims are included in JWT tokens."""
        from .serializers import CustomTokenObtainPairSerializer
        
        # Use the custom serializer to get tokens with custom claims
        refresh = CustomTokenObtainPairSerializer.get_token(self.user)
        
        # Check custom claims in the token
        self.assertEqual(refresh['email'], self.user.email)
        self.assertEqual(refresh['is_admin'], self.user.is_admin)
        self.assertEqual(refresh['full_name'], self.user.get_full_name())

    def test_token_expiration_settings(self):
        """Test that token expiration settings are correctly configured."""
        from django.conf import settings
        from datetime import timedelta
        
        jwt_settings = settings.SIMPLE_JWT
        
        # Check access token lifetime (15 minutes)
        self.assertEqual(jwt_settings['ACCESS_TOKEN_LIFETIME'], timedelta(minutes=15))
        
        # Check refresh token lifetime (7 days)
        self.assertEqual(jwt_settings['REFRESH_TOKEN_LIFETIME'], timedelta(days=7))
        
        # Check token rotation is enabled
        self.assertTrue(jwt_settings['ROTATE_REFRESH_TOKENS'])
        self.assertTrue(jwt_settings['BLACKLIST_AFTER_ROTATION'])


class JWTTokenTest(TestCase):
    """Test cases for JWT token functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_refresh_token_creation(self):
        """Test RefreshToken creation for user."""
        refresh = RefreshToken.for_user(self.user)
        
        self.assertIsInstance(refresh, RefreshToken)
        self.assertEqual(int(refresh['user_id']), self.user.id)

    def test_access_token_from_refresh(self):
        """Test access token generation from refresh token."""
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token
        
        self.assertIsNotNone(access)
        self.assertEqual(int(access['user_id']), self.user.id)

    def test_token_blacklisting(self):
        """Test token blacklisting functionality."""
        refresh = RefreshToken.for_user(self.user)
        token_str = str(refresh)
        
        # Token should be valid initially
        self.assertIsNotNone(token_str)
        
        # Blacklist the token
        refresh.blacklist()
        
        # Token should now be blacklisted
        with self.assertRaises(TokenError):
            RefreshToken(token_str)

    def test_token_string_representation(self):
        """Test token string representation."""
        refresh = RefreshToken.for_user(self.user)
        token_str = str(refresh)
        
        self.assertIsInstance(token_str, str)
        self.assertTrue(len(token_str) > 0)
        
        # Should be able to recreate token from string
        recreated_token = RefreshToken(token_str)
        self.assertEqual(int(recreated_token['user_id']), self.user.id)