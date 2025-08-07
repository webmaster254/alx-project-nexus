"""
Unit tests for jobs serializers.
"""
from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from apps.jobs.serializers import (
    CompanySerializer, JobListSerializer, JobSerializer, JobDetailSerializer
)
from apps.categories.serializers import IndustrySerializer, JobTypeSerializer, CategorySerializer
from tests.base import BaseSerializerTestCase
from tests.factories import (
    CompanyFactory, JobFactory, IndustryFactory, JobTypeFactory, 
    CategoryFactory, AdminUserFactory
)


class CompanySerializerTest(BaseSerializerTestCase):
    """Test cases for CompanySerializer."""
    
    def setUp(self):
        self.valid_data = {
            'name': 'Test Company',
            'description': 'A test company for unit testing',
            'website': 'https://testcompany.com',
            'email': 'contact@testcompany.com',
            'phone': '+1234567890',
            'address': '123 Test Street, Test City, TC 12345',
            'founded_year': 2020,
            'employee_count': '11-50'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = self.assertSerializerValid(CompanySerializer, self.valid_data)
        self.assertEqual(serializer.validated_data['name'], 'Test Company')
        self.assertEqual(serializer.validated_data['website'], 'https://testcompany.com')
    
    def test_read_only_fields(self):
        """Test that read-only fields are not included in validated data."""
        data = self.valid_data.copy()
        data.update({
            'id': 999,
            'slug': 'custom-slug',
            'job_count': 5
        })
        
        serializer = self.assertSerializerValid(CompanySerializer, data)
        self.assertNotIn('id', serializer.validated_data)
        self.assertNotIn('slug', serializer.validated_data)
        self.assertNotIn('job_count', serializer.validated_data)
    
    def test_job_count_field(self):
        """Test job_count computed field."""
        company = CompanyFactory()
        JobFactory.create_batch(3, company=company, is_active=True)
        JobFactory(company=company, is_active=False)  # Inactive job
        
        serializer = CompanySerializer(company)
        self.assertEqual(serializer.data['job_count'], 3)
    
    def test_website_url_validation(self):
        """Test website URL validation."""
        # Valid URLs
        valid_urls = ['https://example.com', 'http://example.com', '']
        for url in valid_urls:
            data = self.valid_data.copy()
            data['website'] = url
            self.assertSerializerValid(CompanySerializer, data)
        
        # Invalid URLs
        invalid_urls = ['not-a-url', 'ftp://example.com']
        for url in invalid_urls:
            data = self.valid_data.copy()
            data['website'] = url
            self.assertSerializerInvalid(CompanySerializer, data, 'website')
    
    def test_email_validation(self):
        """Test email field validation."""
        # Valid emails
        valid_emails = ['test@example.com', 'contact@company.co.uk', '']
        for email in valid_emails:
            data = self.valid_data.copy()
            data['email'] = email
            self.assertSerializerValid(CompanySerializer, data)
        
        # Invalid emails
        invalid_emails = ['invalid-email', '@example.com', 'test@']
        for email in invalid_emails:
            data = self.valid_data.copy()
            data['email'] = email
            self.assertSerializerInvalid(CompanySerializer, data, 'email')
    
    def test_phone_validation(self):
        """Test phone number validation."""
        # Valid phone numbers
        valid_phones = ['+1234567890', '+12345678901234', '']
        for phone in valid_phones:
            data = self.valid_data.copy()
            data['phone'] = phone
            self.assertSerializerValid(CompanySerializer, data)
        
        # Invalid phone numbers
        invalid_phones = ['123', 'abc123']
        for phone in invalid_phones:
            data = self.valid_data.copy()
            data['phone'] = phone
            self.assertSerializerInvalid(CompanySerializer, data, 'phone')


class IndustrySerializerTest(BaseSerializerTestCase):
    """Test cases for IndustrySerializer."""
    
    def test_serializer_with_industry(self):
        """Test serializer with industry instance."""
        industry = IndustryFactory()
        JobFactory.create_batch(2, industry=industry, is_active=True)
        
        serializer = IndustrySerializer(industry)
        self.assertEqual(serializer.data['name'], industry.name)
        self.assertEqual(serializer.data['job_count'], 2)
    
    def test_read_only_fields(self):
        """Test read-only fields."""
        industry = IndustryFactory()
        serializer = IndustrySerializer(industry)
        
        # These should be read-only
        read_only_fields = ['id', 'slug', 'job_count']
        for field in read_only_fields:
            self.assertIn(field, serializer.data)


class JobTypeSerializerTest(BaseSerializerTestCase):
    """Test cases for JobTypeSerializer."""
    
    def test_serializer_with_job_type(self):
        """Test serializer with job type instance."""
        job_type = JobTypeFactory()
        JobFactory.create_batch(3, job_type=job_type, is_active=True)
        
        serializer = JobTypeSerializer(job_type)
        self.assertEqual(serializer.data['name'], job_type.name)
        self.assertEqual(serializer.data['code'], job_type.code)
        self.assertEqual(serializer.data['job_count'], 3)


class CategorySerializerTest(BaseSerializerTestCase):
    """Test cases for CategorySerializer."""
    
    def test_serializer_with_category(self):
        """Test serializer with category instance."""
        category = CategoryFactory()
        JobFactory.create_batch(2, categories=[category], is_active=True)
        
        serializer = CategorySerializer(category)
        self.assertEqual(serializer.data['name'], category.name)
        self.assertEqual(serializer.data['job_count'], 2)
        self.assertEqual(serializer.data['level'], 0)  # Root category


class JobListSerializerTest(BaseSerializerTestCase):
    """Test cases for JobListSerializer."""
    
    def test_serializer_with_job(self):
        """Test serializer with job instance."""
        job = JobFactory(
            title='Software Engineer',
            salary_min=50000,
            salary_max=80000,
            salary_type='yearly',
            salary_currency='USD'
        )
        
        serializer = JobListSerializer(job)
        
        # Test basic fields
        self.assertEqual(serializer.data['title'], 'Software Engineer')
        self.assertEqual(serializer.data['company_name'], job.company.name)
        self.assertEqual(serializer.data['industry_name'], job.industry.name)
        self.assertEqual(serializer.data['job_type_name'], job.job_type.name)
        
        # Test computed fields
        self.assertIn('salary_display', serializer.data)
        self.assertIn('days_since_posted', serializer.data)
        self.assertIn('is_new', serializer.data)
        self.assertIn('can_apply', serializer.data)
    
    def test_read_only_fields(self):
        """Test that all fields are read-only."""
        job = JobFactory()
        serializer = JobListSerializer(job)
        
        # All fields should be read-only in list serializer
        for field_name in serializer.fields:
            field = serializer.fields[field_name]
            self.assertTrue(field.read_only, f"Field {field_name} should be read-only")


class JobSerializerTest(BaseSerializerTestCase):
    """Test cases for JobSerializer."""
    
    def setUp(self):
        self.company = CompanyFactory()
        self.industry = IndustryFactory()
        self.job_type = JobTypeFactory()
        self.categories = CategoryFactory.create_batch(2)
        self.admin_user = AdminUserFactory()
        
        self.valid_data = {
            'title': 'Senior Software Engineer',
            'description': 'We are looking for a senior software engineer...',
            'summary': 'Senior software engineer position',
            'location': 'San Francisco, CA',
            'is_remote': False,
            'salary_min': 80000,
            'salary_max': 120000,
            'salary_type': 'yearly',
            'salary_currency': 'USD',
            'experience_level': 'senior',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'category_ids': [cat.id for cat in self.categories],
            'required_skills_list': ['Python', 'Django', 'PostgreSQL'],
            'preferred_skills_list': ['React', 'Docker'],
            'application_deadline': (timezone.now() + timedelta(days=30)).isoformat()
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = self.assertSerializerValid(JobSerializer, self.valid_data)
        self.assertEqual(serializer.validated_data['title'], 'Senior Software Engineer')
        self.assertEqual(serializer.validated_data['salary_min'], Decimal('80000'))
        self.assertEqual(serializer.validated_data['salary_max'], Decimal('120000'))
    
    def test_company_id_validation(self):
        """Test company_id validation."""
        # Valid company
        serializer = self.assertSerializerValid(JobSerializer, self.valid_data)
        
        # Invalid company ID
        invalid_data = self.valid_data.copy()
        invalid_data['company_id'] = 99999
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'company_id')
        
        # Inactive company
        inactive_company = CompanyFactory(is_active=False)
        invalid_data = self.valid_data.copy()
        invalid_data['company_id'] = inactive_company.id
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'company_id')
    
    def test_industry_id_validation(self):
        """Test industry_id validation."""
        # Invalid industry ID
        invalid_data = self.valid_data.copy()
        invalid_data['industry_id'] = 99999
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'industry_id')
        
        # Inactive industry
        inactive_industry = IndustryFactory(is_active=False)
        invalid_data = self.valid_data.copy()
        invalid_data['industry_id'] = inactive_industry.id
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'industry_id')
    
    def test_job_type_id_validation(self):
        """Test job_type_id validation."""
        # Invalid job type ID
        invalid_data = self.valid_data.copy()
        invalid_data['job_type_id'] = 99999
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'job_type_id')
        
        # Inactive job type
        inactive_job_type = JobTypeFactory(is_active=False)
        invalid_data = self.valid_data.copy()
        invalid_data['job_type_id'] = inactive_job_type.id
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'job_type_id')
    
    def test_category_ids_validation(self):
        """Test category_ids validation."""
        # Valid categories
        serializer = self.assertSerializerValid(JobSerializer, self.valid_data)
        
        # Invalid category ID
        invalid_data = self.valid_data.copy()
        invalid_data['category_ids'] = [99999]
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'category_ids')
        
        # Duplicate category IDs
        invalid_data = self.valid_data.copy()
        invalid_data['category_ids'] = [self.categories[0].id, self.categories[0].id]
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'category_ids')
        
        # Inactive category
        inactive_category = CategoryFactory(is_active=False)
        invalid_data = self.valid_data.copy()
        invalid_data['category_ids'] = [inactive_category.id]
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'category_ids')
    
    def test_application_deadline_validation(self):
        """Test application_deadline validation."""
        # Future deadline (valid)
        future_deadline = timezone.now() + timedelta(days=30)
        data = self.valid_data.copy()
        data['application_deadline'] = future_deadline.isoformat()
        self.assertSerializerValid(JobSerializer, data)
        
        # Past deadline (invalid)
        past_deadline = timezone.now() - timedelta(days=1)
        invalid_data = self.valid_data.copy()
        invalid_data['application_deadline'] = past_deadline.isoformat()
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'application_deadline')
    
    def test_skills_list_validation(self):
        """Test skills list validation."""
        # Valid skills
        serializer = self.assertSerializerValid(JobSerializer, self.valid_data)
        
        # Too many skills
        invalid_data = self.valid_data.copy()
        invalid_data['required_skills_list'] = ['Skill'] * 25
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'required_skills_list')
        
        # Skill too short
        invalid_data = self.valid_data.copy()
        invalid_data['required_skills_list'] = ['A']
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'required_skills_list')
    
    def test_salary_range_validation(self):
        """Test salary range validation."""
        # Valid range
        serializer = self.assertSerializerValid(JobSerializer, self.valid_data)
        
        # Invalid range (min > max)
        invalid_data = self.valid_data.copy()
        invalid_data['salary_min'] = 120000
        invalid_data['salary_max'] = 80000
        self.assertSerializerInvalid(JobSerializer, invalid_data)
        
        # Negative salary
        invalid_data = self.valid_data.copy()
        invalid_data['salary_min'] = -1000
        self.assertSerializerInvalid(JobSerializer, invalid_data, 'salary_min')
    
    def test_create_job(self):
        """Test job creation."""
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.admin_user
        
        context = {'request': request}
        serializer = JobSerializer(data=self.valid_data, context=context)
        self.assertTrue(serializer.is_valid())
        
        job = serializer.save()
        
        # Check job was created correctly
        self.assertEqual(job.title, 'Senior Software Engineer')
        self.assertEqual(job.company, self.company)
        self.assertEqual(job.industry, self.industry)
        self.assertEqual(job.job_type, self.job_type)
        self.assertEqual(job.created_by, self.admin_user)
        self.assertEqual(job.updated_by, self.admin_user)
        
        # Check categories were set
        self.assertEqual(set(job.categories.all()), set(self.categories))
        
        # Check skills were set
        self.assertEqual(job.required_skills, 'Python, Django, PostgreSQL')
        self.assertEqual(job.preferred_skills, 'React, Docker')
    
    def test_update_job(self):
        """Test job update."""
        from rest_framework.test import APIRequestFactory
        
        job = JobFactory()
        
        factory = APIRequestFactory()
        request = factory.put('/')
        request.user = self.admin_user
        
        update_data = {
            'title': 'Updated Title',
            'company_id': self.company.id,
            'industry_id': self.industry.id,
            'job_type_id': self.job_type.id,
            'required_skills_list': ['Updated', 'Skills']
        }
        
        context = {'request': request}
        serializer = JobSerializer(job, data=update_data, partial=True, context=context)
        self.assertTrue(serializer.is_valid())
        
        updated_job = serializer.save()
        
        # Check job was updated correctly
        self.assertEqual(updated_job.title, 'Updated Title')
        self.assertEqual(updated_job.updated_by, self.admin_user)
        self.assertEqual(updated_job.required_skills, 'Updated, Skills')
    
    def test_required_fields(self):
        """Test required fields validation."""
        required_fields = ['title', 'description', 'location', 'company_id', 'industry_id', 'job_type_id']
        
        for field in required_fields:
            invalid_data = self.valid_data.copy()
            invalid_data.pop(field)
            
            self.assertSerializerInvalid(JobSerializer, invalid_data, field)
    
    def test_nested_serializers_in_output(self):
        """Test that nested serializers are used in output."""
        job = JobFactory()
        serializer = JobSerializer(job)
        
        # Check nested serializers
        self.assertIsInstance(serializer.data['company'], dict)
        self.assertIsInstance(serializer.data['industry'], dict)
        self.assertIsInstance(serializer.data['job_type'], dict)
        self.assertIsInstance(serializer.data['categories'], list)
        
        # Check computed fields
        self.assertIn('salary_display', serializer.data)
        self.assertIn('days_since_posted', serializer.data)
        self.assertIn('is_new', serializer.data)
        self.assertIn('can_apply', serializer.data)


class JobDetailSerializerTest(BaseSerializerTestCase):
    """Test cases for JobDetailSerializer."""
    
    def test_additional_fields(self):
        """Test that detail serializer includes additional fields."""
        job = JobFactory(
            required_skills='Python, Django',
            preferred_skills='React, Docker'
        )
        
        serializer = JobDetailSerializer(job)
        
        # Should include all JobSerializer fields plus additional ones
        self.assertIn('required_skills_list', serializer.data)
        self.assertIn('preferred_skills_list', serializer.data)
        self.assertIn('is_application_deadline_passed', serializer.data)
        
        # Check skills lists
        self.assertEqual(serializer.data['required_skills_list'], ['Python', 'Django'])
        self.assertEqual(serializer.data['preferred_skills_list'], ['React', 'Docker'])