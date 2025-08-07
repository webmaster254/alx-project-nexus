"""
Unit tests for categories models.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.categories.models import Industry, JobType, Category
from tests.base import BaseModelTestCase
from tests.factories import IndustryFactory, JobTypeFactory, CategoryFactory, JobFactory


class IndustryModelTest(BaseModelTestCase):
    """Test cases for Industry model."""
    
    def test_industry_creation(self):
        """Test basic industry creation."""
        industry = IndustryFactory()
        self.assertIsInstance(industry, Industry)
        self.assertTrue(industry.is_active)
        self.assertIsNotNone(industry.created_at)
        self.assertIsNotNone(industry.updated_at)
    
    def test_industry_str_representation(self):
        """Test industry string representation."""
        industry = IndustryFactory(name='Technology')
        self.assertEqual(str(industry), 'Technology')
    
    def test_industry_name_uniqueness(self):
        """Test that industry name must be unique."""
        name = 'Technology'
        IndustryFactory(name=name)
        
        with self.assertRaises(IntegrityError):
            IndustryFactory(name=name)
    
    def test_slug_auto_generation(self):
        """Test automatic slug generation from industry name."""
        industry = IndustryFactory(name='Health Care')
        self.assertEqual(industry.slug, 'health-care')
    
    def test_slug_uniqueness(self):
        """Test that industry slug must be unique."""
        IndustryFactory(name='Technology', slug='technology')
        
        with self.assertRaises(IntegrityError):
            IndustryFactory(name='Tech', slug='technology')
    
    def test_job_count_property(self):
        """Test job_count property."""
        industry = IndustryFactory()
        
        # Initially no jobs
        self.assertEqual(industry.job_count, 0)
        
        # Create active jobs
        JobFactory.create_batch(3, industry=industry, is_active=True)
        self.assertEqual(industry.job_count, 3)
        
        # Create inactive job (should not be counted)
        JobFactory(industry=industry, is_active=False)
        self.assertEqual(industry.job_count, 3)
    
    def test_industry_meta_options(self):
        """Test industry model meta options."""
        self.assertEqual(Industry._meta.db_table, 'industry')
        self.assertEqual(Industry._meta.verbose_name, 'Industry')
        self.assertEqual(Industry._meta.verbose_name_plural, 'Industries')
        self.assertEqual(Industry._meta.ordering, ['name'])


class JobTypeModelTest(BaseModelTestCase):
    """Test cases for JobType model."""
    
    def test_job_type_creation(self):
        """Test basic job type creation."""
        job_type = JobTypeFactory()
        self.assertIsInstance(job_type, JobType)
        self.assertTrue(job_type.is_active)
        self.assertIsNotNone(job_type.created_at)
        self.assertIsNotNone(job_type.updated_at)
    
    def test_job_type_str_representation(self):
        """Test job type string representation."""
        job_type = JobTypeFactory(name='Full-time')
        self.assertEqual(str(job_type), 'Full-time')
    
    def test_job_type_name_uniqueness(self):
        """Test that job type name must be unique."""
        name = 'Full-time'
        JobTypeFactory(name=name)
        
        with self.assertRaises(IntegrityError):
            JobTypeFactory(name=name)
    
    def test_job_type_code_uniqueness(self):
        """Test that job type code must be unique."""
        code = 'full-time'
        JobTypeFactory(code=code)
        
        with self.assertRaises(IntegrityError):
            JobTypeFactory(code=code)
    
    def test_slug_auto_generation(self):
        """Test automatic slug generation from job type name."""
        job_type = JobTypeFactory(name='Part Time')
        self.assertEqual(job_type.slug, 'part-time')
    
    def test_employment_type_choices(self):
        """Test employment type choices validation."""
        valid_codes = [
            'full-time', 'part-time', 'contract', 'temporary',
            'internship', 'freelance', 'remote', 'hybrid'
        ]
        
        for code in valid_codes:
            job_type = JobTypeFactory.build(code=code)
            self.assertModelValid(job_type)
    
    def test_job_count_property(self):
        """Test job_count property."""
        job_type = JobTypeFactory()
        
        # Initially no jobs
        self.assertEqual(job_type.job_count, 0)
        
        # Create active jobs
        JobFactory.create_batch(2, job_type=job_type, is_active=True)
        self.assertEqual(job_type.job_count, 2)
        
        # Create inactive job (should not be counted)
        JobFactory(job_type=job_type, is_active=False)
        self.assertEqual(job_type.job_count, 2)
    
    def test_job_type_meta_options(self):
        """Test job type model meta options."""
        self.assertEqual(JobType._meta.db_table, 'job_type')
        self.assertEqual(JobType._meta.verbose_name, 'Job Type')
        self.assertEqual(JobType._meta.verbose_name_plural, 'Job Types')
        self.assertEqual(JobType._meta.ordering, ['name'])


class CategoryModelTest(BaseModelTestCase):
    """Test cases for Category model."""
    
    def test_category_creation(self):
        """Test basic category creation."""
        category = CategoryFactory()
        self.assertIsInstance(category, Category)
        self.assertTrue(category.is_active)
        self.assertIsNone(category.parent)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
    
    def test_category_str_representation(self):
        """Test category string representation."""
        # Root category
        root_category = CategoryFactory(name='Technology')
        self.assertEqual(str(root_category), 'Technology')
        
        # Child category
        child_category = CategoryFactory(name='Software Development', parent=root_category)
        expected_str = 'Technology > Software Development'
        self.assertEqual(str(child_category), expected_str)
    
    def test_slug_auto_generation(self):
        """Test automatic slug generation from category name."""
        category = CategoryFactory(name='Software Development')
        self.assertEqual(category.slug, 'software-development')
    
    def test_hierarchical_slug_generation(self):
        """Test slug generation for hierarchical categories."""
        parent = CategoryFactory(name='Technology', slug='technology')
        child = CategoryFactory(name='Software Development', parent=parent)
        expected_slug = 'technology-software-development'
        self.assertEqual(child.slug, expected_slug)
    
    def test_slug_uniqueness_handling(self):
        """Test slug uniqueness conflict resolution."""
        # Create first category
        CategoryFactory(name='Development', slug='development')
        
        # Create second category with same name (should get unique slug)
        category2 = CategoryFactory(name='Development')
        self.assertNotEqual(category2.slug, 'development')
        self.assertTrue(category2.slug.startswith('development-'))
    
    def test_unique_together_name_parent(self):
        """Test unique_together constraint on name and parent."""
        parent = CategoryFactory()
        CategoryFactory(name='Development', parent=parent)
        
        # Should not be able to create another category with same name and parent
        with self.assertRaises(IntegrityError):
            CategoryFactory(name='Development', parent=parent)
        
        # But should be able to create with different parent
        other_parent = CategoryFactory()
        CategoryFactory(name='Development', parent=other_parent)  # Should work
    
    def test_circular_reference_validation(self):
        """Test prevention of circular references."""
        parent = CategoryFactory()
        child = CategoryFactory(parent=parent)
        
        # Try to make parent a child of child (circular reference)
        parent.parent = child
        self.assertModelInvalid(parent)
    
    def test_self_parent_validation(self):
        """Test prevention of self as parent."""
        category = CategoryFactory()
        category.parent = category
        self.assertModelInvalid(category)
    
    def test_depth_limit_validation(self):
        """Test depth limit validation (max 3 levels)."""
        # Create 3-level hierarchy (should be valid)
        level1 = CategoryFactory(name='Level 1')
        level2 = CategoryFactory(name='Level 2', parent=level1)
        level3 = CategoryFactory(name='Level 3', parent=level2)
        self.assertModelValid(level3)
        
        # Try to create 4th level (should be invalid)
        level4 = CategoryFactory.build(name='Level 4', parent=level3)
        self.assertModelInvalid(level4)
    
    def test_get_ancestors(self):
        """Test get_ancestors method."""
        # Create hierarchy
        root = CategoryFactory(name='Root')
        level1 = CategoryFactory(name='Level 1', parent=root)
        level2 = CategoryFactory(name='Level 2', parent=level1)
        
        # Test ancestors
        ancestors = level2.get_ancestors()
        expected_ancestors = [root, level1]
        self.assertEqual(ancestors, expected_ancestors)
        
        # Root should have no ancestors
        self.assertEqual(root.get_ancestors(), [])
    
    def test_get_descendants(self):
        """Test get_descendants method."""
        # Create hierarchy
        root = CategoryFactory(name='Root')
        child1 = CategoryFactory(name='Child 1', parent=root)
        child2 = CategoryFactory(name='Child 2', parent=root)
        grandchild = CategoryFactory(name='Grandchild', parent=child1)
        
        # Test descendants
        descendants = root.get_descendants()
        expected_descendants = [child1, child2, grandchild]
        self.assertEqual(set(descendants), set(expected_descendants))
        
        # Leaf should have no descendants
        self.assertEqual(grandchild.get_descendants(), [])
    
    def test_get_root(self):
        """Test get_root method."""
        # Create hierarchy
        root = CategoryFactory(name='Root')
        level1 = CategoryFactory(name='Level 1', parent=root)
        level2 = CategoryFactory(name='Level 2', parent=level1)
        
        # All should return same root
        self.assertEqual(root.get_root(), root)
        self.assertEqual(level1.get_root(), root)
        self.assertEqual(level2.get_root(), root)
    
    def test_is_root(self):
        """Test is_root method."""
        root = CategoryFactory(parent=None)
        child = CategoryFactory(parent=root)
        
        self.assertTrue(root.is_root())
        self.assertFalse(child.is_root())
    
    def test_is_leaf(self):
        """Test is_leaf method."""
        parent = CategoryFactory()
        child = CategoryFactory(parent=parent)
        
        self.assertFalse(parent.is_leaf())
        self.assertTrue(child.is_leaf())
    
    def test_get_level(self):
        """Test get_level method."""
        root = CategoryFactory(name='Root')
        level1 = CategoryFactory(name='Level 1', parent=root)
        level2 = CategoryFactory(name='Level 2', parent=level1)
        
        self.assertEqual(root.get_level(), 0)
        self.assertEqual(level1.get_level(), 1)
        self.assertEqual(level2.get_level(), 2)
    
    def test_get_siblings(self):
        """Test get_siblings method."""
        parent = CategoryFactory()
        child1 = CategoryFactory(name='Child 1', parent=parent)
        child2 = CategoryFactory(name='Child 2', parent=parent)
        child3 = CategoryFactory(name='Child 3', parent=parent)
        
        # Test siblings
        siblings = child1.get_siblings()
        expected_siblings = [child2, child3]
        self.assertEqual(set(siblings), set(expected_siblings))
        
        # Root categories
        root1 = CategoryFactory(name='Root 1', parent=None)
        root2 = CategoryFactory(name='Root 2', parent=None)
        
        root_siblings = root1.get_siblings()
        self.assertIn(root2, root_siblings)
        self.assertNotIn(root1, root_siblings)
    
    def test_job_count_property(self):
        """Test job_count property including descendants."""
        # Create hierarchy
        parent = CategoryFactory(name='Parent')
        child = CategoryFactory(name='Child', parent=parent)
        
        # Create jobs in both categories
        JobFactory.create_batch(2, is_active=True).categories.set([parent])
        JobFactory.create_batch(3, is_active=True).categories.set([child])
        
        # Parent should count jobs from itself and descendants
        self.assertEqual(parent.job_count, 5)  # 2 + 3
        
        # Child should count only its own jobs
        self.assertEqual(child.job_count, 3)
        
        # Inactive jobs should not be counted
        inactive_job = JobFactory(is_active=False)
        inactive_job.categories.set([parent])
        self.assertEqual(parent.job_count, 5)  # Still 5
    
    def test_full_path_property(self):
        """Test full_path property."""
        root = CategoryFactory(name='Technology')
        level1 = CategoryFactory(name='Software Development', parent=root)
        level2 = CategoryFactory(name='Frontend Development', parent=level1)
        
        self.assertEqual(root.full_path, 'Technology')
        self.assertEqual(level1.full_path, 'Technology > Software Development')
        self.assertEqual(level2.full_path, 'Technology > Software Development > Frontend Development')
    
    def test_category_meta_options(self):
        """Test category model meta options."""
        self.assertEqual(Category._meta.db_table, 'category')
        self.assertEqual(Category._meta.verbose_name, 'Category')
        self.assertEqual(Category._meta.verbose_name_plural, 'Categories')
        self.assertEqual(Category._meta.ordering, ['name'])
        
        # Test unique_together
        unique_together = Category._meta.unique_together
        self.assertIn(('name', 'parent'), unique_together)
    
    def test_cascade_delete_with_children(self):
        """Test cascade delete behavior with children."""
        parent = CategoryFactory()
        child1 = CategoryFactory(parent=parent)
        child2 = CategoryFactory(parent=parent)
        grandchild = CategoryFactory(parent=child1)
        
        # Store IDs
        child1_id = child1.id
        child2_id = child2.id
        grandchild_id = grandchild.id
        
        # Delete parent
        parent.delete()
        
        # All descendants should be deleted
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=child1_id)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=child2_id)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=grandchild_id)