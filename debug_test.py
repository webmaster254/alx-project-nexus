#!/usr/bin/env python

import os
import sys
sys.path.insert(0, os.getcwd())

# Set up environment similar to production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ['ALLOWED_HOSTS'] = 'jobboard-qump.onrender.com,*.onrender.com,localhost,127.0.0.1'

try:
    import django
    django.setup()
    
    # Test Redis/Cache connection directly
    print('Testing cache connection...')
    from django.core.cache import cache
    try:
        cache.set('test_key', 'test_value', timeout=60)
        result = cache.get('test_key')
        print(f'Cache test: {result}')
        cache.delete('test_key')
    except Exception as e:
        print(f'Cache connection failed: {e}')
        
    # Test database connection
    print('Testing database connection...')
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            print(f'Database test: {result}')
    except Exception as e:
        print(f'Database connection failed: {e}')
    
    from django.test import Client
    
    client = Client()
    
    # Test health endpoint
    response = client.get('/api/health/', HTTP_HOST='jobboard-qump.onrender.com', follow=True)
    print('Health endpoint status:', response.status_code)
    print('Health response:', response.content.decode()[:500])
        
    # Test auth register endpoint with proper JSON data (no trailing slash)
    import json
    response2 = client.post('/api/auth/register', 
        data=json.dumps({
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }),
        HTTP_HOST='jobboard-qump.onrender.com', 
        content_type='application/json'
    )
    print('Register endpoint status (no slash):', response2.status_code)
    print('Register response:', response2.content.decode()[:500])
    
    # Test with trailing slash
    response2b = client.post('/api/auth/register/', 
        data=json.dumps({
            'email': 'test2@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }),
        HTTP_HOST='jobboard-qump.onrender.com', 
        content_type='application/json'
    )
    print('Register endpoint status (with slash):', response2b.status_code)
    print('Register response with slash:', response2b.content.decode()[:500])
    
except Exception as e:
    print('Error during Django setup or health check:', e)
    import traceback
    traceback.print_exc()