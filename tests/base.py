"""
Base test classes providing common testing patterns and utilities.
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
import tempfile
import os
from PIL import Image

from .factories import (
    UserFactory, AdminUserFactory, UserProfileFactory,
    CompanyFactory, JobFactory, CategoryFactory,
    ApplicationFactory, ApplicationStatusFactory
)

User = get_user_model()


class BaseTestCase(TestCase):
    """
    Base test case with common setup and utility methods.
    """
    
    def setUp(self):
        """Set up test data that's commonly needed."""
        self.user = UserFactory()
        self.admin_user = AdminUserFactory()
        
    def create_test_image(self, name='test.jpg', size=(100, 100)):
        """Create a test image file for upload testing."""
        image = Image.new('RGB', size, color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        image.save(temp_file, format='JPEG')
        temp_file.seek(0)
        
        return SimpleUploadedFile(
            name=name,
            content=temp_file.read(),
            content_type='image/jpeg'
        )
    
    def create_test_pdf(self, name='test.pdf', content=b'%PDF-1.4 test content'):
        """Create a test PDF file for upload testing."""
        return SimpleUploadedFile(
            name=name,
            content=content,
            content_type='application/pdf'
        )
    
    def assertFieldError(self, form, field, error_code):
        """Assert that a form field has a specific error."""
        self.assertIn(field, form.errors)
        self.assertIn(error_code, [error.code for error in form.errors[field]])
    
    def assertModelValid(self, model_instance):
        """Assert that a model instance is valid."""
        try:
            model_instance.full_clean()
        except Exception as e:
            self.fail(f"Model validation failed: {e}")
    
    def assertModelInvalid(self, model_instance, field=None):
        """Assert that a model instance is invalid."""
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError) as cm:
            model_instance.full_clean()
        
        if field:
            self.assertIn(field, cm.exception.message_dict)
    
    def tearDown(self):
        """Clean up after tests."""
        # Clean up any uploaded files
        for temp_file in getattr(self, '_temp_files', []):
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class BaseAPITestCase(APITestCase):
    """
    Base API test case with authentication and common API testing utilities.
    """
    
    def setUp(self):
        """Set up API test environment."""
        self.client = APIClient()
        self.user = UserFactory()
        self.admin_user = AdminUserFactory()
        
        # Create default application statuses
        self.pending_status = ApplicationStatusFactory(name='pending')
        self.reviewed_status = ApplicationStatusFactory(name='reviewed')
        self.accepted_status = ApplicationStatusFactory(name='accepted')
        self.rejected_status = ApplicationStatusFactory(name='rejected')
    
    def authenticate_user(self, user=None):
        """Authenticate a user and return the token."""
        if user is None:
            user = self.user
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        return access_token
    
    def authenticate_admin(self):
        """Authenticate as admin user."""
        return self.authenticate_user(self.admin_user)
    
    def unauthenticate(self):
        """Remove authentication credentials."""
        self.client.credentials()
    
    def assertResponseStatus(self, response, expected_status):
        """Assert response has expected status code with detailed error info."""
        if response.status_code != expected_status:
            self.fail(
                f"Expected status {expected_status}, got {response.status_code}. "
                f"Response data: {getattr(response, 'data', response.content)}"
            )
    
    def assertResponseHasKeys(self, response, keys):
        """Assert that response data contains all specified keys."""
        response_data = response.json() if hasattr(response, 'json') else response.data
        for key in keys:
            self.assertIn(key, response_data, f"Key '{key}' not found in response data")
    
    def assertResponseDoesNotHaveKeys(self, response, keys):
        """Assert that response data does not contain specified keys."""
        response_data = response.json() if hasattr(response, 'json') else response.data
        for key in keys:
            self.assertNotIn(key, response_data, f"Key '{key}' found in response data")
    
    def assertPaginatedResponse(self, response, expected_count=None):
        """Assert that response is properly paginated."""
        self.assertResponseStatus(response, 200)
        self.assertResponseHasKeys(response, ['count', 'next', 'previous', 'results'])
        
        if expected_count is not None:
            self.assertEqual(response.data['count'], expected_count)
    
    def assertValidationError(self, response, field=None):
        """Assert that response contains validation errors."""
        self.assertResponseStatus(response, 400)
        if field:
            self.assertIn(field, response.data)
    
    def assertPermissionDenied(self, response):
        """Assert that response indicates permission denied."""
        self.assertIn(response.status_code, [401, 403])
    
    def assertNotFound(self, response):
        """Assert that response indicates resource not found."""
        self.assertResponseStatus(response, 404)


class ModelTestMixin:
    """
    Mixin providing common model testing utilities.
    """
    
    def assertModelFieldRequired(self, model_class, field_name, factory_class):
        """Test that a model field is required."""
        # Create instance without the required field
        kwargs = factory_class._meta.parameters.copy()
        kwargs.pop(field_name, None)
        
        instance = factory_class.build(**kwargs)
        setattr(instance, field_name, None)
        
        self.assertModelInvalid(instance, field_name)
    
    def assertModelFieldMaxLength(self, model_class, field_name, max_length, factory_class):
        """Test that a model field respects max_length constraint."""
        instance = factory_class.build()
        setattr(instance, field_name, 'x' * (max_length + 1))
        
        self.assertModelInvalid(instance, field_name)
    
    def assertModelFieldUnique(self, model_class, field_name, factory_class):
        """Test that a model field is unique."""
        # Create first instance
        instance1 = factory_class.create()
        
        # Try to create second instance with same field value
        instance2 = factory_class.build()
        setattr(instance2, field_name, getattr(instance1, field_name))
        
        with self.assertRaises(Exception):  # Could be ValidationError or IntegrityError
            instance2.save()


class SerializerTestMixin:
    """
    Mixin providing common serializer testing utilities.
    """
    
    def assertSerializerValid(self, serializer_class, data, context=None):
        """Assert that serializer is valid with given data."""
        serializer = serializer_class(data=data, context=context or {})
        if not serializer.is_valid():
            self.fail(f"Serializer validation failed: {serializer.errors}")
        return serializer
    
    def assertSerializerInvalid(self, serializer_class, data, field=None, context=None):
        """Assert that serializer is invalid with given data."""
        serializer = serializer_class(data=data, context=context or {})
        self.assertFalse(serializer.is_valid())
        
        if field:
            self.assertIn(field, serializer.errors)
        
        return serializer
    
    def assertSerializerFieldRequired(self, serializer_class, field_name, valid_data):
        """Test that a serializer field is required."""
        data = valid_data.copy()
        data.pop(field_name, None)
        
        self.assertSerializerInvalid(serializer_class, data, field_name)
    
    def assertSerializerFieldReadOnly(self, serializer_class, field_name, valid_data):
        """Test that a serializer field is read-only."""
        serializer = serializer_class(data=valid_data)
        self.assertNotIn(field_name, serializer.fields)


class APIEndpointTestMixin:
    """
    Mixin providing common API endpoint testing utilities.
    """
    
    def assertListEndpoint(self, url, expected_count=None, auth_required=True):
        """Test a list endpoint."""
        if auth_required:
            # Test unauthenticated access
            response = self.client.get(url)
            self.assertPermissionDenied(response)
            
            # Test authenticated access
            self.authenticate_user()
        
        response = self.client.get(url)
        self.assertPaginatedResponse(response, expected_count)
        return response
    
    def assertCreateEndpoint(self, url, data, auth_required=True, admin_required=False):
        """Test a create endpoint."""
        if auth_required:
            # Test unauthenticated access
            response = self.client.post(url, data)
            self.assertPermissionDenied(response)
            
            if admin_required:
                # Test regular user access
                self.authenticate_user()
                response = self.client.post(url, data)
                self.assertPermissionDenied(response)
                
                # Test admin access
                self.authenticate_admin()
            else:
                self.authenticate_user()
        
        response = self.client.post(url, data)
        self.assertResponseStatus(response, 201)
        return response
    
    def assertRetrieveEndpoint(self, url, auth_required=True):
        """Test a retrieve endpoint."""
        if auth_required:
            # Test unauthenticated access
            response = self.client.get(url)
            self.assertPermissionDenied(response)
            
            # Test authenticated access
            self.authenticate_user()
        
        response = self.client.get(url)
        self.assertResponseStatus(response, 200)
        return response
    
    def assertUpdateEndpoint(self, url, data, auth_required=True, admin_required=False):
        """Test an update endpoint."""
        if auth_required:
            # Test unauthenticated access
            response = self.client.put(url, data)
            self.assertPermissionDenied(response)
            
            if admin_required:
                # Test regular user access
                self.authenticate_user()
                response = self.client.put(url, data)
                self.assertPermissionDenied(response)
                
                # Test admin access
                self.authenticate_admin()
            else:
                self.authenticate_user()
        
        response = self.client.put(url, data)
        self.assertResponseStatus(response, 200)
        return response
    
    def assertDeleteEndpoint(self, url, auth_required=True, admin_required=False):
        """Test a delete endpoint."""
        if auth_required:
            # Test unauthenticated access
            response = self.client.delete(url)
            self.assertPermissionDenied(response)
            
            if admin_required:
                # Test regular user access
                self.authenticate_user()
                response = self.client.delete(url)
                self.assertPermissionDenied(response)
                
                # Test admin access
                self.authenticate_admin()
            else:
                self.authenticate_user()
        
        response = self.client.delete(url)
        self.assertResponseStatus(response, 204)
        return response


class DatabaseTestCase(TransactionTestCase):
    """
    Test case for testing database-specific functionality like transactions.
    """
    
    def setUp(self):
        """Set up database test environment."""
        self.user = UserFactory()
        self.admin_user = AdminUserFactory()
    
    def test_transaction_rollback(self):
        """Test that database transactions work correctly."""
        initial_count = User.objects.count()
        
        try:
            with transaction.atomic():
                UserFactory()
                # Force an error to trigger rollback
                raise Exception("Test rollback")
        except Exception:
            pass
        
        # Count should be unchanged due to rollback
        self.assertEqual(User.objects.count(), initial_count)


class PerformanceTestMixin:
    """
    Mixin for testing performance-related functionality.
    """
    
    def assertQueryCountLessThan(self, max_queries, func, *args, **kwargs):
        """Assert that a function executes with fewer than max_queries database queries."""
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            initial_queries = len(connection.queries)
            func(*args, **kwargs)
            query_count = len(connection.queries) - initial_queries
            
            self.assertLess(
                query_count, max_queries,
                f"Function executed {query_count} queries, expected less than {max_queries}"
            )
    
    def assertQueryCountEqual(self, expected_queries, func, *args, **kwargs):
        """Assert that a function executes exactly the expected number of database queries."""
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            initial_queries = len(connection.queries)
            func(*args, **kwargs)
            query_count = len(connection.queries) - initial_queries
            
            self.assertEqual(
                query_count, expected_queries,
                f"Function executed {query_count} queries, expected {expected_queries}"
            )


# Combined base classes for common use cases

class BaseModelTestCase(BaseTestCase, ModelTestMixin):
    """Combined base class for model testing."""
    pass


class BaseSerializerTestCase(BaseTestCase, SerializerTestMixin):
    """Combined base class for serializer testing."""
    pass


class BaseAPIEndpointTestCase(BaseAPITestCase, APIEndpointTestMixin):
    """Combined base class for API endpoint testing."""
    pass


class BasePerformanceTestCase(BaseTestCase, PerformanceTestMixin):
    """Combined base class for performance testing."""
    pass