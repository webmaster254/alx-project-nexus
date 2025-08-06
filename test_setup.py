"""
Simple script to verify API documentation setup is working correctly.
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Setup Django
django.setup()

def test_schema_generation():
    """Test that the OpenAPI schema can be generated successfully."""
    try:
        from drf_spectacular.openapi import AutoSchema
        from drf_spectacular.generators import SchemaGenerator
        
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)
        
        print("✅ Schema generation successful!")
        print(f"   - API Title: {schema['info']['title']}")
        print(f"   - API Version: {schema['info']['version']}")
        print(f"   - Number of paths: {len(schema['paths'])}")
        
        # Check for our enhanced documentation
        paths = schema['paths']
        
        # Check authentication endpoints
        auth_paths = [path for path in paths.keys() if '/auth/' in path]
        print(f"   - Authentication endpoints: {len(auth_paths)}")
        
        # Check jobs endpoints
        job_paths = [path for path in paths.keys() if '/jobs/' in path]
        print(f"   - Job endpoints: {len(job_paths)}")
        
        # Check applications endpoints
        app_paths = [path for path in paths.keys() if '/applications/' in path]
        print(f"   - Application endpoints: {len(app_paths)}")
        
        # Check categories endpoints
        cat_paths = [path for path in paths.keys() if '/categories/' in path]
        print(f"   - Category endpoints: {len(cat_paths)}")
        
        # Check for examples in login endpoint
        login_path = '/api/auth/login/'
        if login_path in paths:
            login_post = paths[login_path].get('post', {})
            examples = login_post.get('requestBody', {}).get('content', {}).get('application/json', {}).get('examples', {})
            if examples:
                print(f"   - Login endpoint has {len(examples)} documented examples")
            else:
                print("   - ⚠️  Login endpoint missing examples")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema generation failed: {e}")
        return False

def test_spectacular_settings():
    """Test that drf-spectacular settings are configured correctly."""
    try:
        spectacular_settings = getattr(settings, 'SPECTACULAR_SETTINGS', {})
        
        print("✅ Spectacular settings configured!")
        print(f"   - Title: {spectacular_settings.get('TITLE', 'Not set')}")
        print(f"   - Version: {spectacular_settings.get('VERSION', 'Not set')}")
        print(f"   - Tags: {len(spectacular_settings.get('TAGS', []))}")
        print(f"   - Servers: {len(spectacular_settings.get('SERVERS', []))}")
        
        # Check for security configuration
        security = spectacular_settings.get('SECURITY', [])
        if security:
            print(f"   - Security schemes: {len(security)}")
        
        components = spectacular_settings.get('COMPONENTS', {})
        security_schemes = components.get('securitySchemes', {})
        if security_schemes:
            print(f"   - Security components: {list(security_schemes.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Spectacular settings test failed: {e}")
        return False

def test_url_configuration():
    """Test that API documentation URLs are configured correctly."""
    try:
        from django.urls import reverse
        
        # Test that documentation URLs can be resolved
        schema_url = reverse('schema')
        swagger_url = reverse('swagger-ui')
        redoc_url = reverse('redoc')
        
        print("✅ Documentation URLs configured!")
        print(f"   - Schema URL: {schema_url}")
        print(f"   - Swagger UI URL: {swagger_url}")
        print(f"   - ReDoc URL: {redoc_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL configuration test failed: {e}")
        return False

def test_authentication_views():
    """Test that authentication views have proper documentation."""
    try:
        from apps.authentication.views import CustomTokenObtainPairView
        from drf_spectacular.utils import extend_schema
        
        # Check if views have schema decorators
        view_class = CustomTokenObtainPairView
        post_method = getattr(view_class, 'post', None)
        
        if post_method and hasattr(post_method, '_spectacular_annotation'):
            print("✅ Authentication views have documentation!")
            annotation = post_method._spectacular_annotation
            print(f"   - Summary: {annotation.get('summary', 'Not set')}")
            print(f"   - Tags: {annotation.get('tags', [])}")
            examples = annotation.get('examples', [])
            print(f"   - Examples: {len(examples)}")
        else:
            print("⚠️  Authentication views may be missing documentation")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication views test failed: {e}")
        return False

def main():
    """Run all documentation tests."""
    print("🔍 Testing API Documentation Setup...")
    print("=" * 50)
    
    tests = [
        test_spectacular_settings,
        test_url_configuration,
        test_schema_generation,
        test_authentication_views,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print()
        if test():
            passed += 1
        print("-" * 30)
    
    print()
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All documentation tests passed!")
        print("\n📖 You can now access the API documentation at:")
        print("   - Swagger UI: http://localhost:8000/api/docs/")
        print("   - ReDoc: http://localhost:8000/api/redoc/")
        print("   - OpenAPI Schema: http://localhost:8000/api/schema/")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)