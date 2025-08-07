"""
Unit tests for categories serializers.
"""
from django.test import TestCase

from apps.categories.serializers import (
    CategorySerializer, CategoryListSerializer, CategoryHierarchySerializer,
    CategoryWithJobCountSerializer, IndustrySerializer, JobTypeSerializer
)
from tests.base import BaseSerializerTestCase
from tests.factories import (
    CategoryFactory, IndustryFactory, JobTypeFactory, JobFactory
)


class CategorySerializerTest(BaseSerializerTestCase):
    """Test cases for CategorySerializer."""
    
    def setUp(self):
        self.parent_category = CategoryFactory(name='Technology')
        self.valid_data = {
            'name': 'Software Development',
            'description': 'Software development and programming jobs',
            'parent': self.parent_category.id
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = self.assertSerializerValid(CategorySerializer, self.valid_data)
        self.assertEqual(serializer.validated_data['name'], 'Software Development')
        self.assertEqual(serializer.validated_data['parent'], self.parent_category)
    
    def test_serializer_with_category_instance(self):
        """Test serializer with category instance."""
        child_category = CategoryFactory(name='Frontend Development', parent=self.parent_category)
        grandchild = CategoryFactory(name='React Development', parent=child_category)
        
        # Create jobs for testing job_count
        JobFactory.create_batch(2, categories=[child_category], is_active=True)
        JobFactory.create_batch(1, categories=[grandchild], is_active=True)
        
        serializer = CategorySerializer(child_category)
        
        # Test basic fields
        self.assertEqual(serializer.data['name'], 'Frontend Development')
        self.assertEqual(serializer.data['parent'], self.parent_category.id)
        self.assertEqual(serializer.data['parent_name'], 'Technology')
        
        # Test computed fields
        self.assertEqual(serializer.data['job_count'], 3)  # 2 direct + 1 from descendant
        self.assertEqual(serializer.data['full_path'], 'Technology > Frontend Development')
        self.assertEqual(serializer.data['level'], 1)
        
        # Test children
        self.assertIn('children', serializer.data)
        self.assertEqual(len(serializer.data['children']), 1)
    
    def test_read_only_fields(self):
        """Test read-only fields."""
        category = CategoryFactory()
        serializer = CategorySerializer(category)
        
        read_only_fields = [
            'id', 'slug', 'job_count', 'full_path', 'level', 
            'children', 'parent_name', 'created_at', 'updated_at'
        ]
        for field in read_only_fields:
            self.assertTrue(serializer.fields[field].read_only)
    
    def test_parent_validation_inactive_parent(self):
        """Test parent validation with inactive parent."""
        inactive_parent = CategoryFactory(is_active=False)
        
        invalid_data = self.valid_data.copy()
        invalid_data['parent'] = inactive_parent.id
        
        self.assertSerializerInvalid(CategorySerializer, invalid_data, 'parent')
    
    def test_parent_validation_circular_reference(self):
        """Test parent validation prevents circular references."""
        # Create a category
        category = CategoryFactory(name='Test Category')
        child = CategoryFactory(name='Child Category', parent=category)
        
        # Try to make category a child of its own child (circular reference)
        invalid_data = {
            'name': 'Test Category',
            'parent': child.id
        }
        
        serializer = CategorySerializer(category, data=invalid_data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('parent', serializer.errors)
    
    def test_parent_validation_depth_limit(self):
        """Test parent validation enforces depth limit."""
        # Create 3-level hierarchy
        level1 = CategoryFactory(name='Level 1')
        level2 = CategoryFactory(name='Level 2', parent=level1)
        level3 = CategoryFactory(name='Level 3', parent=level2)
        
        # Try to create 4th level (should fail)
        invalid_data = {
            'name': 'Level 4',
            'parent': level3.id
        }
        
        serializer = CategorySerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('parent', serializer.errors)
    
    def test_get_children_method(self):
        """Test get_children method."""
        parent = CategoryFactory(name='Parent')
        active_child = CategoryFactory(name='Active Child', parent=parent, is_active=True)
        inactive_child = CategoryFactory(name='Inactive Child', parent=parent, is_active=False)
        
        serializer = CategorySerializer(parent)
        
        # Should only include active children
        children_data = serializer.data['children']
        self.assertEqual(len(children_data), 1)
        self.assertEqual(children_data[0]['name'], 'Active Child')


class CategoryListSerializerTest(BaseSerializerTestCase):
    """Test cases for CategoryListSerializer."""
    
    def test_serializer_with_category(self):
        """Test serializer with category instance."""
        parent = CategoryFactory(name='Technology')
        category = CategoryFactory(name='Software Development', parent=parent)
        JobFactory.create_batch(2, categories=[category], is_active=True)
        
        serializer = CategoryListSerializer(category)
        
        # Test basic fields
        self.assertEqual(serializer.data['name'], 'Software Development')
        self.assertEqual(serializer.data['parent'], parent.id)
        self.assertEqual(serializer.data['parent_name'], 'Technology')
        
        # Test computed fields
        self.assertEqual(serializer.data['job_count'], 2)
        self.assertEqual(serializer.data['full_path'], 'Technology > Software Development')
        self.assertEqual(serializer.data['level'], 1)
    
    def test_read_only_fields(self):
        """Test read-only fields."""
        category = CategoryFactory()
        serializer = CategoryListSerializer(category)
        
        read_only_fields = ['id', 'slug', 'job_count', 'full_path', 'level', 'parent_name']
        for field in read_only_fields:
            self.assertTrue(serializer.fields[field].read_only)


class CategoryHierarchySerializerTest(BaseSerializerTestCase):
    """Test cases for CategoryHierarchySerializer."""
    
    def test_serializer_with_hierarchy(self):
        """Test serializer with hierarchical categories."""
        # Create hierarchy
        root = CategoryFactory(name='Technology')
        child1 = CategoryFactory(name='Software Development', parent=root)
        child2 = CategoryFactory(name='Design', parent=root)
        grandchild = CategoryFactory(name='Frontend Development', parent=child1)
        
        # Create jobs
        JobFactory.create_batch(1, categories=[root], is_active=True)  # Direct job
        JobFactory.create_batch(2, categories=[child1], is_active=True)
        JobFactory.create_batch(1, categories=[grandchild], is_active=True)
        
        serializer = CategoryHierarchySerializer(root)
        
        # Test basic fields
        self.assertEqual(serializer.data['name'], 'Technology')
        self.assertEqual(serializer.data['direct_job_count'], 1)
        self.assertEqual(serializer.data['total_job_count'], 4)  # 1 + 2 + 1
        
        # Test nested children
        children = serializer.data['children']
        self.assertEqual(len(children), 2)
        
        # Find software development child
        software_dev = next(child for child in children if child['name'] == 'Software Development')
        self.assertEqual(software_dev['direct_job_count'], 2)
        self.assertEqual(software_dev['total_job_count'], 3)  # 2 + 1 from grandchild
        
        # Test grandchildren
        grandchildren = software_dev['children']
        self.assertEqual(len(grandchildren), 1)
        self.assertEqual(grandchildren[0]['name'], 'Frontend Development')
    
    def test_get_children_method(self):
        """Test get_children method only includes active categories."""
        parent = CategoryFactory(name='Parent')
        active_child = CategoryFactory(name='Active Child', parent=parent, is_active=True)
        inactive_child = CategoryFactory(name='Inactive Child', parent=parent, is_active=False)
        
        serializer = CategoryHierarchySerializer(parent)
        
        # Should only include active children
        children = serializer.data['children']
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0]['name'], 'Active Child')


class CategoryWithJobCountSerializerTest(BaseSerializerTestCase):
    """Test cases for CategoryWithJobCountSerializer."""
    
    def test_serializer_with_job_counts(self):
        """Test serializer with job count information."""
        parent = CategoryFactory(name='Technology')
        child = CategoryFactory(name='Software Development', parent=parent)
        
        # Create jobs
        JobFactory.create_batch(2, categories=[parent], is_active=True)  # Direct jobs
        JobFactory.create_batch(3, categories=[child], is_active=True)   # Child jobs
        JobFactory(categories=[parent], is_active=False)  # Inactive job (shouldn't count)
        
        serializer = CategoryWithJobCountSerializer(parent)
        
        # Test job counts
        self.assertEqual(serializer.data['direct_job_count'], 2)
        self.assertEqual(serializer.data['job_count'], 5)  # 2 direct + 3 from child
        
        # Test other fields
        self.assertEqual(serializer.data['name'], 'Technology')
        self.assertEqual(serializer.data['level'], 0)
        self.assertEqual(serializer.data['full_path'], 'Technology')


class IndustrySerializerTest(BaseSerializerTestCase):
    """Test cases for IndustrySerializer."""
    
    def setUp(self):
        self.valid_data = {
            'name': 'Technology',
            'description': 'Technology and software companies'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = self.assertSerializerValid(IndustrySerializer, self.valid_data)
        self.assertEqual(serializer.validated_data['name'], 'Technology')
        self.assertEqual(serializer.validated_data['description'], 'Technology and software companies')
    
    def test_serializer_with_industry_instance(self):
        """Test serializer with industry instance."""
        industry = IndustryFactory(name='Healthcare')
        JobFactory.create_batch(3, industry=industry, is_active=True)
        JobFactory(industry=industry, is_active=False)  # Inactive job
        
        serializer = IndustrySerializer(industry)
        
        self.assertEqual(serializer.data['name'], 'Healthcare')
        self.assertEqual(serializer.data['job_count'], 3)  # Only active jobs
    
    def test_read_only_fields(self):
        """Test read-only fields."""
        industry = IndustryFactory()
        serializer = IndustrySerializer(industry)
        
        read_only_fields = ['id', 'slug', 'job_count', 'created_at', 'updated_at']
        for field in read_only_fields:
            self.assertTrue(serializer.fields[field].read_only)
    
    def test_required_fields(self):
        """Test required fields validation."""
        # Name is required
        invalid_data = self.valid_data.copy()
        invalid_data.pop('name')
        
        self.assertSerializerInvalid(IndustrySerializer, invalid_data, 'name')
        
        # Description is optional
        valid_data = self.valid_data.copy()
        valid_data.pop('description')
        
        self.assertSerializerValid(IndustrySerializer, valid_data)
    
    def test_name_max_length(self):
        """Test name field max length validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['name'] = 'x' * 101  # Exceeds max_length of 100
        
        self.assertSerializerInvalid(IndustrySerializer, invalid_data, 'name')


class JobTypeSerializerTest(BaseSerializerTestCase):
    """Test cases for JobTypeSerializer."""
    
    def setUp(self):
        self.valid_data = {
            'name': 'Full-time',
            'code': 'full-time',
            'description': 'Full-time employment position'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = self.assertSerializerValid(JobTypeSerializer, self.valid_data)
        self.assertEqual(serializer.validated_data['name'], 'Full-time')
        self.assertEqual(serializer.validated_data['code'], 'full-time')
    
    def test_serializer_with_job_type_instance(self):
        """Test serializer with job type instance."""
        job_type = JobTypeFactory(name='Part-time', code='part-time')
        JobFactory.create_batch(2, job_type=job_type, is_active=True)
        JobFactory(job_type=job_type, is_active=False)  # Inactive job
        
        serializer = JobTypeSerializer(job_type)
        
        self.assertEqual(serializer.data['name'], 'Part-time')
        self.assertEqual(serializer.data['code'], 'part-time')
        self.assertEqual(serializer.data['job_count'], 2)  # Only active jobs
    
    def test_read_only_fields(self):
        """Test read-only fields."""
        job_type = JobTypeFactory()
        serializer = JobTypeSerializer(job_type)
        
        read_only_fields = ['id', 'slug', 'job_count', 'created_at', 'updated_at']
        for field in read_only_fields:
            self.assertTrue(serializer.fields[field].read_only)
    
    def test_required_fields(self):
        """Test required fields validation."""
        # Name is required
        invalid_data = self.valid_data.copy()
        invalid_data.pop('name')
        
        self.assertSerializerInvalid(JobTypeSerializer, invalid_data, 'name')
        
        # Code is required
        invalid_data = self.valid_data.copy()
        invalid_data.pop('code')
        
        self.assertSerializerInvalid(JobTypeSerializer, invalid_data, 'code')
        
        # Description is optional
        valid_data = self.valid_data.copy()
        valid_data.pop('description')
        
        self.assertSerializerValid(JobTypeSerializer, valid_data)
    
    def test_name_max_length(self):
        """Test name field max length validation."""
        invalid_data = self.valid_data.copy()
        invalid_data['name'] = 'x' * 51  # Exceeds max_length of 50
        
        self.assertSerializerInvalid(JobTypeSerializer, invalid_data, 'name')
    
    def test_code_choices_validation(self):
        """Test code field choices validation."""
        valid_codes = [
            'full-time', 'part-time', 'contract', 'temporary',
            'internship', 'freelance', 'remote', 'hybrid'
        ]
        
        for code in valid_codes:
            data = self.valid_data.copy()
            data['code'] = code
            self.assertSerializerValid(JobTypeSerializer, data)