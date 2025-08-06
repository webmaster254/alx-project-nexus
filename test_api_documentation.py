#!/usr/bin/env python
"""
Test script to verify API documentation functionality.
"""
import os
import sys
import django
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()


class APIDocumentationTest(TestCase):
    """Test API documentation endpoints."""
    
    def setUp(self):
        self.client = Client()
    
    def test_schema_endpoint_accessible(self):
        """Test that the schema endpoint is accessible."""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/vnd.oai.openapi')
    
    def test_swagger_ui_accessible(self):
        """Test that the Swagger UI endpoint is accessible."""
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Swagger UI')
        self.assertContains(response, 'Job Board API')
    
    def test_redoc_accessible(self):
        """Test that the ReDoc endpoint is accessible."""
        response = self.client.get('/api/redoc/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ReDoc')
        self.assertContains(response, 'Job Board API')
    
    def test_schema_contains_authentication_info(self):
        """Test that the schema contains JWT authentication information."""
        response = self.client.get('/api/schema/')
        schema_content = response.content.decode('utf-8')
        
        # Check for JWT authentication components
        self.assertIn('bearerAuth', schema_content)
        self.assertIn('JWT', schema_content)
        self.assertIn('Authentication', schema_content)
    
    def test_schema_contains_api_endpoints(self):
        """Test that the schema contains expected API endpoints."""
        response = self.client.get('/api/schema/')
        schema_content = response.content.decode('utf-8')
        
        # Check for main API endpoints
        self.assertIn('/api/auth/', schema_content)
        self.assertIn('/api/jobs/', schema_content)
        self.assertIn('/api/applications/', schema_content)
        self.assertIn('/api/categories/', schema_content)


if __name__ == '__main__':
    import unittest
    
    # Run the tests
    suite = unittest.TestLoader().loadTestsFromTestCase(APIDocumentationTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)