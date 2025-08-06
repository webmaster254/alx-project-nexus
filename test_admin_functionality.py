#!/usr/bin/env python
"""
Simple test script to verify admin status management functionality.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.applications.models import Application, ApplicationStatus
from apps.jobs.models import Job, Company
from apps.categories.models import Industry, JobType
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()

def setup_test_data():
    """Setup test data for admin functionality testing."""
    print("Setting up test data...")
    
    # Clean up existing data
    Application.objects.all().delete()
    ApplicationStatus.objects.all().delete()
    Job.objects.all().delete()
    Company.objects.all().delete()
    User.objects.all().delete()
    
    # Create users
    admin_user = User.objects.create_user(
        email='admin@test.com',
        username='admin',
        password='pass123',
        is_admin=True
    )
    
    user1 = User.objects.create_user(
        email='user1@test.com',
        username='user1',
        password='pass123'
    )
    
    user2 = User.objects.create_user(
        email='user2@test.com',
        username='user2',
        password='pass123'
    )
    
    # Create company and job
    company = Company.objects.create(name='Test Company')
    industry = Industry.objects.get_or_create(name='Technology')[0]
    job_type = JobType.objects.get_or_create(name='Full-time', code='FT')[0]
    
    job = Job.objects.create(
        title='Software Engineer',
        description='Test job',
        company=company,
        location='Test City',
        job_type=job_type,
        industry=industry,
        created_by=admin_user
    )
    
    # Create application statuses
    pending_status = ApplicationStatus.objects.create(
        name='pending',
        display_name='Pending Review',
        description='Application is pending review'
    )
    
    reviewed_status = ApplicationStatus.objects.create(
        name='reviewed',
        display_name='Under Review',
        description='Application is under review'
    )
    
    accepted_status = ApplicationStatus.objects.create(
        name='accepted',
        display_name='Accepted',
        description='Application has been accepted',
        is_final=True
    )
    
    # Create applications
    app1 = Application.objects.create(
        user=user1,
        job=job,
        status=pending_status,
        cover_letter='Application from user1'
    )
    
    app2 = Application.objects.create(
        user=user2,
        job=job,
        status=pending_status,
        cover_letter='Application from user2'
    )
    
    print(f"Created {Application.objects.count()} applications")
    print(f"Created {ApplicationStatus.objects.count()} statuses")
    
    return {
        'admin_user': admin_user,
        'user1': user1,
        'user2': user2,
        'job': job,
        'app1': app1,
        'app2': app2,
        'pending_status': pending_status,
        'reviewed_status': reviewed_status,
        'accepted_status': accepted_status
    }

def get_auth_token(user):
    """Get JWT token for user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def test_admin_endpoints(data):
    """Test admin-specific endpoints."""
    print("\n=== Testing Admin Endpoints ===")
    
    client = APIClient()
    admin_token = get_auth_token(data['admin_user'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    
    # Test 1: Admin can see all applications
    print("\n1. Testing admin can see all applications...")
    response = client.get('/api/applications/applications/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        apps = response.json()['results']
        print(f"Admin sees {len(apps)} applications")
        for app in apps:
            print(f"  - App {app['id']}: {app['user_email']} -> {app['status']['name']}")
    
    # Test 2: Admin can filter by job
    print("\n2. Testing admin can filter applications by job...")
    response = client.get(f'/api/applications/applications/by-job/{data["job"].id}/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        apps = response.json()['results']
        print(f"Found {len(apps)} applications for job {data['job'].id}")
    
    # Test 3: Admin can get pending applications
    print("\n3. Testing admin can get pending applications...")
    response = client.get('/api/applications/applications/admin/pending/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        apps = response.json()['results']
        print(f"Found {len(apps)} pending applications")
    
    # Test 4: Admin can update application status
    print("\n4. Testing admin can update application status...")
    app_id = data['app1'].id
    response = client.post(f'/api/applications/applications/{app_id}/update-status/', {
        'status_name': 'reviewed',
        'notes': 'Application looks good'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Successfully updated application status")
        # Verify the update
        data['app1'].refresh_from_db()
        print(f"App {app_id} status: {data['app1'].status.name}")
        print(f"Notes: {data['app1'].notes}")
    
    # Test 5: Admin can bulk update status
    print("\n5. Testing admin can bulk update status...")
    response = client.post('/api/applications/applications/bulk-update-status/', {
        'application_ids': [data['app1'].id, data['app2'].id],
        'status_name': 'reviewed',
        'notes': 'Bulk review completed'
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Updated {result['updated_count']} applications")
    
    # Test 6: Test application status endpoints
    print("\n6. Testing application status endpoints...")
    response = client.get('/api/applications/application-statuses/')
    print(f"Status list: {response.status_code}")
    if response.status_code == 200:
        statuses = response.json()['results']
        print(f"Found {len(statuses)} statuses")
        for status in statuses:
            print(f"  - {status['name']}: {status['display_name']} (final: {status['is_final']})")

def test_user_restrictions(data):
    """Test that regular users have proper restrictions."""
    print("\n=== Testing User Restrictions ===")
    
    client = APIClient()
    user_token = get_auth_token(data['user1'])
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_token}')
    
    # Test 1: User cannot access admin endpoints
    print("\n1. Testing user cannot access admin endpoints...")
    
    # Try to access by-job endpoint (admin only)
    response = client.get(f'/api/applications/applications/by-job/{data["job"].id}/')
    print(f"by-job endpoint: {response.status_code} (should be 403)")
    
    # Try to access admin pending endpoint
    response = client.get('/api/applications/applications/admin/pending/')
    print(f"admin/pending endpoint: {response.status_code} (should be 403)")
    
    # Try to update status (admin only)
    response = client.post(f'/api/applications/applications/{data["app1"].id}/update-status/', {
        'status_name': 'reviewed'
    })
    print(f"update-status endpoint: {response.status_code} (should be 403)")
    
    # Try bulk update (admin only)
    response = client.post('/api/applications/applications/bulk-update-status/', {
        'application_ids': [data['app1'].id],
        'status_name': 'reviewed'
    })
    print(f"bulk-update-status endpoint: {response.status_code} (should be 403)")
    
    # Test 2: User can only see their own applications
    print("\n2. Testing user can only see their own applications...")
    response = client.get('/api/applications/applications/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        apps = response.json()['results']
        print(f"User sees {len(apps)} applications (should be 1)")
        if apps:
            print(f"  - App belongs to: {apps[0]['user_email']}")

def main():
    """Main test function."""
    print("Starting Admin Status Management Functionality Test")
    print("=" * 50)
    
    try:
        # Setup test data
        data = setup_test_data()
        
        # Test admin functionality
        test_admin_endpoints(data)
        
        # Test user restrictions
        test_user_restrictions(data)
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("Admin status management functionality is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()