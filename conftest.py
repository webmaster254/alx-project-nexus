"""
Pytest configuration and fixtures for the job board backend project.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def pytest_configure():
    """Configure Django settings for pytest."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """Set up the test database."""
    pass


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests.
    This fixture is automatically used for all tests.
    """
    pass


@pytest.fixture
def api_client():
    """Provide an API client for testing."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def user_factory():
    """Provide UserFactory for tests."""
    from tests.factories import UserFactory
    return UserFactory


@pytest.fixture
def admin_user_factory():
    """Provide AdminUserFactory for tests."""
    from tests.factories import AdminUserFactory
    return AdminUserFactory


@pytest.fixture
def job_factory():
    """Provide JobFactory for tests."""
    from tests.factories import JobFactory
    return JobFactory


@pytest.fixture
def application_factory():
    """Provide ApplicationFactory for tests."""
    from tests.factories import ApplicationFactory
    return ApplicationFactory


@pytest.fixture
def company_factory():
    """Provide CompanyFactory for tests."""
    from tests.factories import CompanyFactory
    return CompanyFactory


@pytest.fixture
def category_factory():
    """Provide CategoryFactory for tests."""
    from tests.factories import CategoryFactory
    return CategoryFactory


@pytest.fixture
def industry_factory():
    """Provide IndustryFactory for tests."""
    from tests.factories import IndustryFactory
    return IndustryFactory


@pytest.fixture
def job_type_factory():
    """Provide JobTypeFactory for tests."""
    from tests.factories import JobTypeFactory
    return JobTypeFactory


@pytest.fixture
def application_status_factory():
    """Provide ApplicationStatusFactory for tests."""
    from tests.factories import ApplicationStatusFactory
    return ApplicationStatusFactory


@pytest.fixture
def authenticated_user(api_client, user_factory):
    """Provide an authenticated user and client."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    user = user_factory()
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    return user, api_client


@pytest.fixture
def authenticated_admin(api_client, admin_user_factory):
    """Provide an authenticated admin user and client."""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    admin = admin_user_factory()
    refresh = RefreshToken.for_user(admin)
    access_token = str(refresh.access_token)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    return admin, api_client


@pytest.fixture
def test_data_setup():
    """Set up basic test data."""
    from tests.fixtures import load_test_fixtures
    load_test_fixtures()


@pytest.fixture
def sample_job_data():
    """Provide sample job data for testing."""
    return {
        'title': 'Senior Software Engineer',
        'description': 'We are looking for a senior software engineer...',
        'summary': 'Senior software engineer position',
        'location': 'San Francisco, CA',
        'is_remote': False,
        'salary_min': 120000,
        'salary_max': 150000,
        'salary_type': 'yearly',
        'salary_currency': 'USD',
        'experience_level': 'senior',
        'required_skills': 'Python, Django, PostgreSQL',
        'preferred_skills': 'Docker, AWS, React',
    }


@pytest.fixture
def sample_application_data():
    """Provide sample application data for testing."""
    return {
        'cover_letter': 'I am very interested in this position...',
        'notes': '',
    }


@pytest.fixture
def sample_user_data():
    """Provide sample user data for testing."""
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
    }


@pytest.fixture
def sample_company_data():
    """Provide sample company data for testing."""
    return {
        'name': 'Test Company Inc.',
        'description': 'A test company for testing purposes',
        'website': 'https://testcompany.com',
        'email': 'contact@testcompany.com',
        'phone': '+1-555-123-4567',
        'address': '123 Test Street, Test City, TC 12345',
        'founded_year': 2010,
        'employee_count': '50-100',
    }


# Pytest markers for organizing tests
pytest_plugins = [
    'pytest_django',
]


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location and name."""
    for item in items:
        # Mark tests in specific directories
        if 'unit' in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif 'integration' in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif 'api' in str(item.fspath):
            item.add_marker(pytest.mark.api)
        
        # Mark tests based on name patterns
        if 'test_auth' in item.name or 'authentication' in str(item.fspath):
            item.add_marker(pytest.mark.auth)
        elif 'test_job' in item.name or 'jobs' in str(item.fspath):
            item.add_marker(pytest.mark.jobs)
        elif 'test_application' in item.name or 'applications' in str(item.fspath):
            item.add_marker(pytest.mark.applications)
        elif 'test_category' in item.name or 'categories' in str(item.fspath):
            item.add_marker(pytest.mark.categories)
        elif 'test_search' in item.name or 'search' in item.name:
            item.add_marker(pytest.mark.search)
        elif 'test_admin' in item.name or 'admin' in item.name:
            item.add_marker(pytest.mark.admin)
        elif 'performance' in item.name:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)