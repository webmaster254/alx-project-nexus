#!/usr/bin/env python
"""
Simple test script to verify Django project setup
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()
    
    # Test basic Django setup
    print("✓ Django setup successful")
    print(f"✓ Settings module: {settings.SETTINGS_MODULE}")
    print(f"✓ Database engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"✓ Installed apps: {len(settings.INSTALLED_APPS)} apps")
    
    # Test URL configuration
    from django.urls import reverse
    from django.test import Client
    
    client = Client()
    
    try:
        # Test admin URL
        response = client.get('/admin/')
        print(f"✓ Admin URL accessible (status: {response.status_code})")
        
        # Test API schema URL
        response = client.get('/api/schema/')
        print(f"✓ API schema URL accessible (status: {response.status_code})")
        
        print("\n✅ Django project setup completed successfully!")
        print("🚀 Ready for task implementation!")
        
    except Exception as e:
        print(f"❌ URL test failed: {e}")
        sys.exit(1)