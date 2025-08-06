from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils.text import slugify
from .models import Industry, JobType, Category


class IndustryModelTest(TestCase):
    """Test cases for the Industry model."""

    def setUp(self):
        """Set up test data."""
        self.industry_data = {
            'name': 'Technology',
            'description': 'Software development, IT services, and technology companies'
        }

    def test_create_industry(self):
        """Test creating an industry with all fields."""
        industry = Industry.objects.create(**self.industry_data)
        
        self.assertEqual(industry.name, 'Technology')
        self.assertEqual(industry.description, 'Software development, IT services, and technology companies')
        self.assertTrue(industry.is_active)
        self.assertIsNotNone(industry.created_at)
        self.assertIsNotNone(industry.updated_at)

    def test_create_industry_minimal(self):
        """Test creating an industry with only required fields."""
        industry = Industry.objects.create(name='Healthcare')
        
        self.assertEqual(industry.name, 'Healthcare')
        self.assertEqual(industry.description, '')
        self.assertTrue(industry.is_active)

    def test_industry_name_unique_constraint(self):
        """Test that industry name must be unique."""
        Industry.objects.create(name='Finance')
        
        with self.assertRaises(IntegrityError):
            Industry.objects.create(name='Finance')

    def test_industry_name_max_length(self):
        """Test industry name max length validation."""
        long_name = 'A' * 101  # Exceeds max_length of 100
        industry = Industry(name=long_name)
        
        with self.assertRaises(ValidationError):
            industry.full_clean()

    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from industry name."""
        industry = Industry.objects.create(name='Information Technology')
        expected_slug = slugify('Information Technology')
        self.assertEqual(industry.slug, expected_slug)

    def test_slug_unique_constraint(self):
        """Test that slug must be unique."""
        Industry.objects.create(name='Technology', slug='tech')
        
        with self.assertRaises(IntegrityError):
            Industry.objects.create(name='Tech Industry', slug='tech')

    def test_custom_slug(self):
        """Test creating industry with custom slug."""
        industry = Industry.objects.create(
            name='Technology',
            slug='custom-tech-slug'
        )
        self.assertEqual(industry.slug, 'custom-tech-slug')

    def test_str_representation(self):
        """Test string representation of industry."""
        industry = Industry.objects.create(name='Technology')
        self.assertEqual(str(industry), 'Technology')

    def test_job_count_property(self):
        """Test job_count property (will be 0 until Job model is implemented)."""
        industry = Industry.objects.create(name='Technology')
        # Since Job model isn't implemented yet, this should return 0
        self.assertEqual(industry.job_count, 0)

    def test_is_active_field(self):
        """Test is_active field functionality."""
        industry = Industry.objects.create(name='Technology')
        self.assertTrue(industry.is_active)
        
        industry.is_active = False
        industry.save()
        industry.refresh_from_db()
        self.assertFalse(industry.is_active)

    def test_ordering(self):
        """Test model ordering by name."""
        Industry.objects.create(name='Zebra Industry')
        Industry.objects.create(name='Alpha Industry')
        Industry.objects.create(name='Beta Industry')
        
        industries = list(Industry.objects.all())
        industry_names = [industry.name for industry in industries]
        
        self.assertEqual(industry_names, ['Alpha Industry', 'Beta Industry', 'Zebra Industry'])


class JobTypeModelTest(TestCase):
    """Test cases for the JobType model."""

    def setUp(self):
        """Set up test data."""
        self.job_type_data = {
            'name': 'Full-time',
            'code': 'full-time',
            'description': 'Full-time employment with standard working hours'
        }

    def test_create_job_type(self):
        """Test creating a job type with all fields."""
        job_type = JobType.objects.create(**self.job_type_data)
        
        self.assertEqual(job_type.name, 'Full-time')
        self.assertEqual(job_type.code, 'full-time')
        self.assertEqual(job_type.description, 'Full-time employment with standard working hours')
        self.assertTrue(job_type.is_active)
        self.assertIsNotNone(job_type.created_at)
        self.assertIsNotNone(job_type.updated_at)

    def test_create_job_type_minimal(self):
        """Test creating a job type with only required fields."""
        job_type = JobType.objects.create(name='Part-time', code='part-time')
        
        self.assertEqual(job_type.name, 'Part-time')
        self.assertEqual(job_type.code, 'part-time')
        self.assertEqual(job_type.description, '')
        self.assertTrue(job_type.is_active)

    def test_job_type_name_unique_constraint(self):
        """Test that job type name must be unique."""
        JobType.objects.create(name='Contract', code='contract')
        
        with self.assertRaises(IntegrityError):
            JobType.objects.create(name='Contract', code='contract-2')

    def test_job_type_code_unique_constraint(self):
        """Test that job type code must be unique."""
        JobType.objects.create(name='Remote Work', code='remote')
        
        with self.assertRaises(IntegrityError):
            JobType.objects.create(name='Remote Position', code='remote')

    def test_job_type_name_max_length(self):
        """Test job type name max length validation."""
        long_name = 'A' * 51  # Exceeds max_length of 50
        job_type = JobType(name=long_name, code='test')
        
        with self.assertRaises(ValidationError):
            job_type.full_clean()

    def test_job_type_code_max_length(self):
        """Test job type code max length validation."""
        long_code = 'a' * 21  # Exceeds max_length of 20
        job_type = JobType(name='Test Type', code=long_code)
        
        with self.assertRaises(ValidationError):
            job_type.full_clean()

    def test_employment_type_choices(self):
        """Test that code field accepts valid employment type choices."""
        valid_codes = [
            'full-time', 'part-time', 'contract', 'temporary',
            'internship', 'freelance', 'remote', 'hybrid'
        ]
        
        for code in valid_codes:
            job_type_data = self.job_type_data.copy()
            job_type_data['code'] = code
            job_type_data['name'] = f'Test {code}'
            job_type = JobType(**job_type_data)
            try:
                job_type.full_clean()
            except ValidationError:
                self.fail(f"Valid employment type code {code} failed validation")

    def test_invalid_employment_type_choice(self):
        """Test that code field rejects invalid employment type choices."""
        invalid_codes = ['invalid-type', 'unknown', 'custom-type']
        
        for code in invalid_codes:
            job_type_data = self.job_type_data.copy()
            job_type_data['code'] = code
            job_type = JobType(**job_type_data)
            with self.assertRaises(ValidationError):
                job_type.full_clean()

    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from job type name."""
        job_type = JobType.objects.create(name='Full-time Position', code='full-time')
        expected_slug = slugify('Full-time Position')
        self.assertEqual(job_type.slug, expected_slug)

    def test_slug_unique_constraint(self):
        """Test that slug must be unique."""
        JobType.objects.create(name='Full-time', code='full-time', slug='fulltime')
        
        with self.assertRaises(IntegrityError):
            JobType.objects.create(name='Fulltime', code='part-time', slug='fulltime')

    def test_custom_slug(self):
        """Test creating job type with custom slug."""
        job_type = JobType.objects.create(
            name='Full-time',
            code='full-time',
            slug='custom-fulltime-slug'
        )
        self.assertEqual(job_type.slug, 'custom-fulltime-slug')

    def test_str_representation(self):
        """Test string representation of job type."""
        job_type = JobType.objects.create(name='Full-time', code='full-time')
        self.assertEqual(str(job_type), 'Full-time')

    def test_job_count_property(self):
        """Test job_count property (will be 0 until Job model is implemented)."""
        job_type = JobType.objects.create(name='Full-time', code='full-time')
        # Since Job model isn't implemented yet, this should return 0
        self.assertEqual(job_type.job_count, 0)

    def test_is_active_field(self):
        """Test is_active field functionality."""
        job_type = JobType.objects.create(name='Full-time', code='full-time')
        self.assertTrue(job_type.is_active)
        
        job_type.is_active = False
        job_type.save()
        job_type.refresh_from_db()
        self.assertFalse(job_type.is_active)

    def test_ordering(self):
        """Test model ordering by name."""
        JobType.objects.create(name='Zebra Type', code='zebra')
        JobType.objects.create(name='Alpha Type', code='alpha')
        JobType.objects.create(name='Beta Type', code='beta')
        
        job_types = list(JobType.objects.all())
        job_type_names = [job_type.name for job_type in job_types]
        
        self.assertEqual(job_type_names, ['Alpha Type', 'Beta Type', 'Zebra Type'])

    def test_employment_types_constant(self):
        """Test that EMPLOYMENT_TYPES constant contains expected values."""
        expected_types = [
            ('full-time', 'Full-time'),
            ('part-time', 'Part-time'),
            ('contract', 'Contract'),
            ('temporary', 'Temporary'),
            ('internship', 'Internship'),
            ('freelance', 'Freelance'),
            ('remote', 'Remote'),
            ('hybrid', 'Hybrid'),
        ]
        
        self.assertEqual(JobType.EMPLOYMENT_TYPES, expected_types)


class CategoryModelTest(TestCase):
    """Test cases for the Category model."""

    def setUp(self):
        """Set up test data."""
        self.category_data = {
            'name': 'Technology',
            'description': 'Technology-related job categories'
        }

    def test_create_category(self):
        """Test creating a category with all fields."""
        category = Category.objects.create(**self.category_data)
        
        self.assertEqual(category.name, 'Technology')
        self.assertEqual(category.description, 'Technology-related job categories')
        self.assertTrue(category.is_active)
        self.assertIsNone(category.parent)
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)

    def test_create_category_minimal(self):
        """Test creating a category with only required fields."""
        category = Category.objects.create(name='Marketing')
        
        self.assertEqual(category.name, 'Marketing')
        self.assertEqual(category.description, '')
        self.assertTrue(category.is_active)
        self.assertIsNone(category.parent)

    def test_category_name_max_length(self):
        """Test category name max length validation."""
        long_name = 'A' * 101  # Exceeds max_length of 100
        category = Category(name=long_name)
        
        with self.assertRaises(ValidationError):
            category.full_clean()

    def test_slug_auto_generation(self):
        """Test that slug is auto-generated from category name."""
        category = Category.objects.create(name='Software Development')
        expected_slug = slugify('Software Development')
        self.assertEqual(category.slug, expected_slug)

    def test_slug_auto_generation_with_parent(self):
        """Test that slug includes parent slug when category has parent."""
        parent = Category.objects.create(name='Technology')
        child = Category.objects.create(name='Software Development', parent=parent)
        expected_slug = f"{parent.slug}-{slugify('Software Development')}"
        self.assertEqual(child.slug, expected_slug)

    def test_slug_unique_constraint(self):
        """Test that slug must be unique."""
        Category.objects.create(name='Technology', slug='tech')
        
        with self.assertRaises(ValidationError):
            Category.objects.create(name='Tech Industry', slug='tech')

    def test_slug_conflict_resolution(self):
        """Test that slug conflicts are resolved by appending numbers."""
        # Create first category
        cat1 = Category.objects.create(name='Technology')
        
        # Create second category with same name (different parent to avoid unique_together constraint)
        parent = Category.objects.create(name='Parent')
        cat2 = Category.objects.create(name='Technology', parent=parent)
        
        # The second category should have a different slug
        self.assertNotEqual(cat1.slug, cat2.slug)
        self.assertTrue(cat2.slug.startswith('parent-technology'))

    def test_custom_slug(self):
        """Test creating category with custom slug."""
        category = Category.objects.create(
            name='Technology',
            slug='custom-tech-slug'
        )
        self.assertEqual(category.slug, 'custom-tech-slug')

    def test_unique_together_name_parent(self):
        """Test that name and parent combination must be unique."""
        parent = Category.objects.create(name='Technology')
        Category.objects.create(name='Software', parent=parent)
        
        # Should not be able to create another 'Software' under same parent
        with self.assertRaises(ValidationError):
            Category.objects.create(name='Software', parent=parent)

    def test_same_name_different_parents(self):
        """Test that same name can exist under different parents."""
        parent1 = Category.objects.create(name='Technology')
        parent2 = Category.objects.create(name='Business')
        
        # Should be able to create 'Development' under both parents
        cat1 = Category.objects.create(name='Development', parent=parent1)
        cat2 = Category.objects.create(name='Development', parent=parent2)
        
        self.assertEqual(cat1.name, cat2.name)
        self.assertNotEqual(cat1.parent, cat2.parent)

    def test_str_representation_root(self):
        """Test string representation of root category."""
        category = Category.objects.create(name='Technology')
        self.assertEqual(str(category), 'Technology')

    def test_str_representation_child(self):
        """Test string representation of child category."""
        parent = Category.objects.create(name='Technology')
        child = Category.objects.create(name='Software Development', parent=parent)
        self.assertEqual(str(child), 'Technology > Software Development')

    def test_str_representation_grandchild(self):
        """Test string representation of grandchild category."""
        grandparent = Category.objects.create(name='Technology')
        parent = Category.objects.create(name='Software', parent=grandparent)
        child = Category.objects.create(name='Web Development', parent=parent)
        self.assertEqual(str(child), 'Technology > Software > Web Development')

    def test_circular_reference_prevention_direct(self):
        """Test prevention of direct circular reference (self as parent)."""
        category = Category.objects.create(name='Technology')
        category.parent = category
        
        with self.assertRaises(ValidationError) as context:
            category.save()
        
        self.assertIn("circular references", str(context.exception))

    def test_circular_reference_prevention_indirect(self):
        """Test prevention of indirect circular reference."""
        parent = Category.objects.create(name='Technology')
        child = Category.objects.create(name='Software', parent=parent)
        
        # Try to make parent a child of child (circular reference)
        parent.parent = child
        
        with self.assertRaises(ValidationError) as context:
            parent.save()
        
        self.assertIn("circular references", str(context.exception))

    def test_depth_limit_validation(self):
        """Test that category hierarchy cannot exceed 3 levels deep."""
        level1 = Category.objects.create(name='Technology')
        level2 = Category.objects.create(name='Software', parent=level1)
        level3 = Category.objects.create(name='Web Development', parent=level2)
        
        # This should work (3 levels)
        self.assertEqual(level3.get_level(), 2)
        
        # Try to create 4th level (should fail)
        level4 = Category(name='Frontend', parent=level3)
        with self.assertRaises(ValidationError) as context:
            level4.save()
        
        self.assertIn("cannot exceed 3 levels", str(context.exception))

    def test_get_ancestors(self):
        """Test getting all ancestor categories."""
        grandparent = Category.objects.create(name='Technology')
        parent = Category.objects.create(name='Software', parent=grandparent)
        child = Category.objects.create(name='Web Development', parent=parent)
        
        ancestors = child.get_ancestors()
        self.assertEqual(len(ancestors), 2)
        self.assertEqual(ancestors[0], grandparent)
        self.assertEqual(ancestors[1], parent)

    def test_get_ancestors_root(self):
        """Test getting ancestors for root category."""
        root = Category.objects.create(name='Technology')
        ancestors = root.get_ancestors()
        self.assertEqual(len(ancestors), 0)

    def test_get_descendants(self):
        """Test getting all descendant categories."""
        grandparent = Category.objects.create(name='Technology')
        parent1 = Category.objects.create(name='Software', parent=grandparent)
        parent2 = Category.objects.create(name='Hardware', parent=grandparent)
        child1 = Category.objects.create(name='Web Development', parent=parent1)
        child2 = Category.objects.create(name='Mobile Development', parent=parent1)
        
        descendants = grandparent.get_descendants()
        self.assertEqual(len(descendants), 4)
        self.assertIn(parent1, descendants)
        self.assertIn(parent2, descendants)
        self.assertIn(child1, descendants)
        self.assertIn(child2, descendants)

    def test_get_descendants_leaf(self):
        """Test getting descendants for leaf category."""
        parent = Category.objects.create(name='Technology')
        leaf = Category.objects.create(name='Software', parent=parent)
        
        descendants = leaf.get_descendants()
        self.assertEqual(len(descendants), 0)

    def test_get_root(self):
        """Test getting root category."""
        grandparent = Category.objects.create(name='Technology')
        parent = Category.objects.create(name='Software', parent=grandparent)
        child = Category.objects.create(name='Web Development', parent=parent)
        
        self.assertEqual(child.get_root(), grandparent)
        self.assertEqual(parent.get_root(), grandparent)
        self.assertEqual(grandparent.get_root(), grandparent)

    def test_is_root(self):
        """Test checking if category is root."""
        root = Category.objects.create(name='Technology')
        child = Category.objects.create(name='Software', parent=root)
        
        self.assertTrue(root.is_root())
        self.assertFalse(child.is_root())

    def test_is_leaf(self):
        """Test checking if category is leaf."""
        parent = Category.objects.create(name='Technology')
        child = Category.objects.create(name='Software', parent=parent)
        
        self.assertFalse(parent.is_leaf())
        self.assertTrue(child.is_leaf())

    def test_get_level(self):
        """Test getting category level in hierarchy."""
        level0 = Category.objects.create(name='Technology')
        level1 = Category.objects.create(name='Software', parent=level0)
        level2 = Category.objects.create(name='Web Development', parent=level1)
        
        self.assertEqual(level0.get_level(), 0)
        self.assertEqual(level1.get_level(), 1)
        self.assertEqual(level2.get_level(), 2)

    def test_get_siblings(self):
        """Test getting sibling categories."""
        parent = Category.objects.create(name='Technology')
        child1 = Category.objects.create(name='Software', parent=parent)
        child2 = Category.objects.create(name='Hardware', parent=parent)
        child3 = Category.objects.create(name='Networking', parent=parent)
        
        siblings = child1.get_siblings()
        self.assertEqual(len(siblings), 2)
        self.assertIn(child2, siblings)
        self.assertIn(child3, siblings)
        self.assertNotIn(child1, siblings)

    def test_get_siblings_root(self):
        """Test getting siblings for root categories."""
        root1 = Category.objects.create(name='Technology')
        root2 = Category.objects.create(name='Business')
        root3 = Category.objects.create(name='Healthcare')
        
        siblings = root1.get_siblings()
        self.assertEqual(len(siblings), 2)
        self.assertIn(root2, siblings)
        self.assertIn(root3, siblings)
        self.assertNotIn(root1, siblings)

    def test_job_count_property(self):
        """Test job_count property (will be 0 until Job model is implemented)."""
        category = Category.objects.create(name='Technology')
        # Since Job model isn't implemented yet, this should return 0
        self.assertEqual(category.job_count, 0)

    def test_full_path_property(self):
        """Test full_path property for hierarchical path display."""
        grandparent = Category.objects.create(name='Technology')
        parent = Category.objects.create(name='Software', parent=grandparent)
        child = Category.objects.create(name='Web Development', parent=parent)
        
        self.assertEqual(grandparent.full_path, 'Technology')
        self.assertEqual(parent.full_path, 'Technology > Software')
        self.assertEqual(child.full_path, 'Technology > Software > Web Development')

    def test_is_active_field(self):
        """Test is_active field functionality."""
        category = Category.objects.create(name='Technology')
        self.assertTrue(category.is_active)
        
        category.is_active = False
        category.save()
        category.refresh_from_db()
        self.assertFalse(category.is_active)

    def test_ordering(self):
        """Test model ordering by name."""
        Category.objects.create(name='Zebra Category')
        Category.objects.create(name='Alpha Category')
        Category.objects.create(name='Beta Category')
        
        categories = list(Category.objects.all())
        category_names = [category.name for category in categories]
        
        self.assertEqual(category_names, ['Alpha Category', 'Beta Category', 'Zebra Category'])

    def test_cascade_delete(self):
        """Test that deleting parent category deletes children."""
        parent = Category.objects.create(name='Technology')
        child1 = Category.objects.create(name='Software', parent=parent)
        child2 = Category.objects.create(name='Hardware', parent=parent)
        
        # Verify children exist
        self.assertEqual(Category.objects.filter(parent=parent).count(), 2)
        
        # Delete parent
        parent.delete()
        
        # Verify children are also deleted
        self.assertFalse(Category.objects.filter(pk=child1.pk).exists())
        self.assertFalse(Category.objects.filter(pk=child2.pk).exists())

    def test_related_name_children(self):
        """Test that children related name works correctly."""
        parent = Category.objects.create(name='Technology')
        child1 = Category.objects.create(name='Software', parent=parent)
        child2 = Category.objects.create(name='Hardware', parent=parent)
        
        children = parent.children.all()
        self.assertEqual(len(children), 2)
        self.assertIn(child1, children)
        self.assertIn(child2, children)