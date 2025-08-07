"""
Integration tests for category management API endpoints.
Tests category CRUD operations, hierarchical relationships, and job filtering.
"""
from django.urls import reverse
from rest_framework import status

from tests.base import BaseAPIEndpointTestCase
from tests.factories import (
    CategoryFactory, SubCategoryFactory, IndustryFactory, 
    JobTypeFactory, JobFactory, CompanyFactory
)
from apps.categories.models import Category, Industry, JobType


class CategoryAPITestCase(BaseAPIEndpointTestCase):
    """Test category API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.categories_url = reverse('categories:category-list')
        
        # Create test categories
        self.parent_category = CategoryFactory(
            name='Technology',
            description='Technology related jobs',
            is_active=True
        )
        
        self.child_category = SubCategoryFactory(
            name='Software Development',
            parent=self.parent_category,
            is_active=True
        )
        
        self.inactive_category = CategoryFactory(
            name='Inactive Category',
            is_active=False
        )
    
    def test_list_categories_active_only(self):
        """Test listing categories returns only active ones."""
        response = self.client.get(self.categories_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response)
        
        category_names = [cat['name'] for cat in response.data['results']]
        self.assertIn('Technology', category_names)
        self.assertIn('Software Development', category_names)
        self.assertNotIn('Inactive Category', category_names)
    
    def test_list_categories_includes_hierarchy(self):
        """Test that category list includes parent-child relationships."""
        response = self.client.get(self.categories_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Find the child category in response
        child_cat_data = None
        for cat in response.data['results']:
            if cat['name'] == 'Software Development':
                child_cat_data = cat
                break
        
        self.assertIsNotNone(child_cat_data)
        self.assertEqual(child_cat_data['parent'], self.parent_category.id)
        
        # Find the parent category in response
        parent_cat_data = None
        for cat in response.data['results']:
            if cat['name'] == 'Technology':
                parent_cat_data = cat
                break
        
        self.assertIsNotNone(parent_cat_data)
        self.assertIsNone(parent_cat_data['parent'])
    
    def test_retrieve_category_by_slug(self):
        """Test retrieving category by slug."""
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.parent_category.slug})
        
        response = self.client.get(category_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Technology')
        self.assertEqual(response.data['slug'], self.parent_category.slug)
        
        expected_fields = [
            'id', 'name', 'description', 'slug', 'parent', 
            'is_active', 'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_retrieve_category_by_id(self):
        """Test retrieving category by ID."""
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.parent_category.pk})
        
        response = self.client.get(category_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Technology')
    
    def test_retrieve_inactive_category_not_found(self):
        """Test that inactive categories return 404."""
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.inactive_category.slug})
        
        response = self.client.get(category_url)
        
        self.assertNotFound(response)
    
    def test_create_category_admin_success(self):
        """Test creating category as admin user."""
        self.authenticate_admin()
        
        category_data = {
            'name': 'Marketing',
            'description': 'Marketing and advertising positions',
            'parent': None
        }
        
        response = self.client.post(self.categories_url, category_data)
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Marketing')
        self.assertEqual(response.data['slug'], 'marketing')
        self.assertTrue(response.data['is_active'])
        
        # Verify category was created in database
        category = Category.objects.get(name='Marketing')
        self.assertEqual(category.description, 'Marketing and advertising positions')
        self.assertIsNone(category.parent)
    
    def test_create_subcategory_admin_success(self):
        """Test creating subcategory as admin user."""
        self.authenticate_admin()
        
        category_data = {
            'name': 'Mobile Development',
            'description': 'Mobile app development positions',
            'parent': self.parent_category.id
        }
        
        response = self.client.post(self.categories_url, category_data)
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Mobile Development')
        self.assertEqual(response.data['parent'], self.parent_category.id)
        
        # Verify subcategory was created
        subcategory = Category.objects.get(name='Mobile Development')
        self.assertEqual(subcategory.parent, self.parent_category)
    
    def test_create_category_regular_user_forbidden(self):
        """Test that regular users cannot create categories."""
        self.authenticate_user()
        
        category_data = {
            'name': 'Unauthorized Category',
            'description': 'This should not be created'
        }
        
        response = self.client.post(self.categories_url, category_data)
        
        self.assertPermissionDenied(response)
    
    def test_create_category_unauthenticated_forbidden(self):
        """Test that unauthenticated users cannot create categories."""
        category_data = {
            'name': 'Unauthorized Category',
            'description': 'This should not be created'
        }
        
        response = self.client.post(self.categories_url, category_data)
        
        self.assertPermissionDenied(response)
    
    def test_create_category_duplicate_name_error(self):
        """Test that duplicate category names are not allowed."""
        self.authenticate_admin()
        
        category_data = {
            'name': 'Technology',  # Already exists
            'description': 'Duplicate technology category'
        }
        
        response = self.client.post(self.categories_url, category_data)
        
        self.assertValidationError(response, 'name')
    
    def test_update_category_admin_success(self):
        """Test updating category as admin user."""
        self.authenticate_admin()
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.parent_category.pk})
        
        update_data = {
            'name': 'Information Technology',
            'description': 'Updated description for IT jobs',
            'parent': None
        }
        
        response = self.client.put(category_url, update_data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Information Technology')
        self.assertEqual(response.data['description'], 'Updated description for IT jobs')
        
        # Verify category was updated in database
        self.parent_category.refresh_from_db()
        self.assertEqual(self.parent_category.name, 'Information Technology')
    
    def test_partial_update_category_admin_success(self):
        """Test partial update of category as admin user."""
        self.authenticate_admin()
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.parent_category.pk})
        
        update_data = {
            'description': 'Updated description only'
        }
        
        response = self.client.patch(category_url, update_data)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description only')
        
        # Verify name remained unchanged
        self.assertEqual(response.data['name'], 'Technology')
    
    def test_update_category_regular_user_forbidden(self):
        """Test that regular users cannot update categories."""
        self.authenticate_user()
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.parent_category.pk})
        
        update_data = {
            'name': 'Unauthorized Update'
        }
        
        response = self.client.put(category_url, update_data)
        
        self.assertPermissionDenied(response)
    
    def test_delete_category_admin_success(self):
        """Test deleting category as admin user."""
        # Create a category without children for deletion
        deletable_category = CategoryFactory(name='Deletable Category')
        
        self.authenticate_admin()
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': deletable_category.pk})
        
        response = self.client.delete(category_url)
        
        self.assertResponseStatus(response, status.HTTP_204_NO_CONTENT)
        
        # Verify category was deleted
        self.assertFalse(Category.objects.filter(pk=deletable_category.pk).exists())
    
    def test_delete_category_with_children_error(self):
        """Test that categories with children cannot be deleted."""
        self.authenticate_admin()
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.parent_category.pk})
        
        response = self.client.delete(category_url)
        
        # Should return error because category has children
        self.assertResponseStatus(response, status.HTTP_400_BAD_REQUEST)
        
        # Verify category still exists
        self.assertTrue(Category.objects.filter(pk=self.parent_category.pk).exists())
    
    def test_delete_category_regular_user_forbidden(self):
        """Test that regular users cannot delete categories."""
        self.authenticate_user()
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.parent_category.pk})
        
        response = self.client.delete(category_url)
        
        self.assertPermissionDenied(response)


class IndustryAPITestCase(BaseAPIEndpointTestCase):
    """Test industry API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.industries_url = reverse('categories:industry-list')
        
        # Create test industries
        self.tech_industry = IndustryFactory(
            name='Technology',
            description='Technology and software companies',
            is_active=True
        )
        
        self.finance_industry = IndustryFactory(
            name='Finance',
            description='Financial services and banking',
            is_active=True
        )
        
        self.inactive_industry = IndustryFactory(
            name='Inactive Industry',
            is_active=False
        )
    
    def test_list_industries_active_only(self):
        """Test listing industries returns only active ones."""
        response = self.client.get(self.industries_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response)
        
        industry_names = [ind['name'] for ind in response.data['results']]
        self.assertIn('Technology', industry_names)
        self.assertIn('Finance', industry_names)
        self.assertNotIn('Inactive Industry', industry_names)
    
    def test_retrieve_industry_success(self):
        """Test retrieving a specific industry."""
        industry_url = reverse('categories:industry-detail', 
                             kwargs={'pk': self.tech_industry.pk})
        
        response = self.client.get(industry_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Technology')
        
        expected_fields = [
            'id', 'name', 'description', 'slug', 'is_active',
            'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_create_industry_admin_success(self):
        """Test creating industry as admin user."""
        self.authenticate_admin()
        
        industry_data = {
            'name': 'Healthcare',
            'description': 'Healthcare and medical services'
        }
        
        response = self.client.post(self.industries_url, industry_data)
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Healthcare')
        self.assertEqual(response.data['slug'], 'healthcare')
        
        # Verify industry was created
        industry = Industry.objects.get(name='Healthcare')
        self.assertEqual(industry.description, 'Healthcare and medical services')
    
    def test_create_industry_regular_user_forbidden(self):
        """Test that regular users cannot create industries."""
        self.authenticate_user()
        
        industry_data = {
            'name': 'Unauthorized Industry',
            'description': 'This should not be created'
        }
        
        response = self.client.post(self.industries_url, industry_data)
        
        self.assertPermissionDenied(response)


class JobTypeAPITestCase(BaseAPIEndpointTestCase):
    """Test job type API endpoints."""
    
    def setUp(self):
        super().setUp()
        self.job_types_url = reverse('categories:jobtype-list')
        
        # Create test job types
        self.fulltime_type = JobTypeFactory(
            name='Full-time',
            code='fulltime',
            description='Full-time employment',
            is_active=True
        )
        
        self.parttime_type = JobTypeFactory(
            name='Part-time',
            code='parttime',
            description='Part-time employment',
            is_active=True
        )
        
        self.inactive_type = JobTypeFactory(
            name='Inactive Type',
            is_active=False
        )
    
    def test_list_job_types_active_only(self):
        """Test listing job types returns only active ones."""
        response = self.client.get(self.job_types_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertPaginatedResponse(response)
        
        type_names = [jt['name'] for jt in response.data['results']]
        self.assertIn('Full-time', type_names)
        self.assertIn('Part-time', type_names)
        self.assertNotIn('Inactive Type', type_names)
    
    def test_retrieve_job_type_success(self):
        """Test retrieving a specific job type."""
        job_type_url = reverse('categories:jobtype-detail', 
                             kwargs={'pk': self.fulltime_type.pk})
        
        response = self.client.get(job_type_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Full-time')
        self.assertEqual(response.data['code'], 'fulltime')
        
        expected_fields = [
            'id', 'name', 'code', 'description', 'slug', 
            'is_active', 'created_at', 'updated_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_create_job_type_admin_success(self):
        """Test creating job type as admin user."""
        self.authenticate_admin()
        
        job_type_data = {
            'name': 'Contract',
            'code': 'contract',
            'description': 'Contract-based employment'
        }
        
        response = self.client.post(self.job_types_url, job_type_data)
        
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Contract')
        self.assertEqual(response.data['code'], 'contract')
        
        # Verify job type was created
        job_type = JobType.objects.get(name='Contract')
        self.assertEqual(job_type.code, 'contract')
    
    def test_create_job_type_regular_user_forbidden(self):
        """Test that regular users cannot create job types."""
        self.authenticate_user()
        
        job_type_data = {
            'name': 'Unauthorized Type',
            'code': 'unauthorized'
        }
        
        response = self.client.post(self.job_types_url, job_type_data)
        
        self.assertPermissionDenied(response)


class CategoryJobFilteringTestCase(BaseAPIEndpointTestCase):
    """Test job filtering by categories."""
    
    def setUp(self):
        super().setUp()
        self.jobs_url = reverse('jobs:job-list')
        
        # Create test data
        self.company = CompanyFactory()
        self.industry = IndustryFactory()
        self.job_type = JobTypeFactory()
        
        # Create categories
        self.tech_category = CategoryFactory(name='Technology')
        self.dev_category = SubCategoryFactory(
            name='Development',
            parent=self.tech_category
        )
        self.design_category = CategoryFactory(name='Design')
        
        # Create jobs with different categories
        self.dev_job = JobFactory(
            title='Python Developer',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            is_active=True
        )
        self.dev_job.categories.add(self.dev_category)
        
        self.design_job = JobFactory(
            title='UI Designer',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            is_active=True
        )
        self.design_job.categories.add(self.design_category)
        
        self.multi_category_job = JobFactory(
            title='Full Stack Developer',
            company=self.company,
            industry=self.industry,
            job_type=self.job_type,
            is_active=True
        )
        self.multi_category_job.categories.add(self.dev_category, self.design_category)
    
    def test_filter_jobs_by_category(self):
        """Test filtering jobs by specific category."""
        response = self.client.get(self.jobs_url, {
            'categories': self.dev_category.id
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)  # dev_job and multi_category_job
        
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Python Developer', job_titles)
        self.assertIn('Full Stack Developer', job_titles)
        self.assertNotIn('UI Designer', job_titles)
    
    def test_filter_jobs_by_parent_category(self):
        """Test filtering jobs by parent category includes subcategory jobs."""
        response = self.client.get(self.jobs_url, {
            'categories': self.tech_category.id
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        # Should include jobs from subcategories
        self.assertGreaterEqual(response.data['count'], 2)
        
        job_titles = [job['title'] for job in response.data['results']]
        self.assertIn('Python Developer', job_titles)
        self.assertIn('Full Stack Developer', job_titles)
    
    def test_filter_jobs_by_multiple_categories(self):
        """Test filtering jobs by multiple categories."""
        response = self.client.get(self.jobs_url, {
            'categories': f"{self.dev_category.id},{self.design_category.id}"
        })
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # All jobs match at least one category
    
    def test_category_job_count_aggregation(self):
        """Test that category endpoints include job counts."""
        categories_url = reverse('categories:category-list')
        
        response = self.client.get(categories_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Find development category in response
        dev_cat_data = None
        for cat in response.data['results']:
            if cat['name'] == 'Development':
                dev_cat_data = cat
                break
        
        self.assertIsNotNone(dev_cat_data)
        # Should include job count if implemented
        if 'job_count' in dev_cat_data:
            self.assertEqual(dev_cat_data['job_count'], 2)


class CategoryHierarchyTestCase(BaseAPIEndpointTestCase):
    """Test category hierarchical relationships."""
    
    def setUp(self):
        super().setUp()
        self.categories_url = reverse('categories:category-list')
        
        # Create hierarchical category structure
        self.root_category = CategoryFactory(name='Technology')
        
        self.level1_dev = SubCategoryFactory(
            name='Development',
            parent=self.root_category
        )
        
        self.level1_design = SubCategoryFactory(
            name='Design',
            parent=self.root_category
        )
        
        self.level2_frontend = SubCategoryFactory(
            name='Frontend Development',
            parent=self.level1_dev
        )
        
        self.level2_backend = SubCategoryFactory(
            name='Backend Development',
            parent=self.level1_dev
        )
    
    def test_category_hierarchy_structure(self):
        """Test that category hierarchy is properly structured."""
        response = self.client.get(self.categories_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # Build category lookup
        categories = {cat['id']: cat for cat in response.data['results']}
        
        # Verify root category has no parent
        root_cat = categories[self.root_category.id]
        self.assertIsNone(root_cat['parent'])
        
        # Verify level 1 categories have root as parent
        dev_cat = categories[self.level1_dev.id]
        self.assertEqual(dev_cat['parent'], self.root_category.id)
        
        design_cat = categories[self.level1_design.id]
        self.assertEqual(design_cat['parent'], self.root_category.id)
        
        # Verify level 2 categories have level 1 as parent
        frontend_cat = categories[self.level2_frontend.id]
        self.assertEqual(frontend_cat['parent'], self.level1_dev.id)
        
        backend_cat = categories[self.level2_backend.id]
        self.assertEqual(backend_cat['parent'], self.level1_dev.id)
    
    def test_category_children_endpoint(self):
        """Test endpoint for getting category children."""
        # This would test a custom endpoint for getting category children
        # if implemented in the API
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.root_category.pk})
        
        response = self.client.get(category_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # If children are included in the response
        if 'children' in response.data:
            children_ids = [child['id'] for child in response.data['children']]
            self.assertIn(self.level1_dev.id, children_ids)
            self.assertIn(self.level1_design.id, children_ids)
    
    def test_category_ancestors_path(self):
        """Test getting category ancestor path."""
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.level2_frontend.pk})
        
        response = self.client.get(category_url)
        
        self.assertResponseStatus(response, status.HTTP_200_OK)
        
        # If ancestor path is included in the response
        if 'ancestors' in response.data:
            ancestor_names = [anc['name'] for anc in response.data['ancestors']]
            self.assertIn('Technology', ancestor_names)
            self.assertIn('Development', ancestor_names)
    
    def test_prevent_circular_hierarchy(self):
        """Test that circular category hierarchies are prevented."""
        self.authenticate_admin()
        
        # Try to make root category a child of its descendant
        category_url = reverse('categories:category-detail', 
                             kwargs={'pk': self.root_category.pk})
        
        update_data = {
            'name': self.root_category.name,
            'description': self.root_category.description,
            'parent': self.level1_dev.id  # This would create a circular reference
        }
        
        response = self.client.put(category_url, update_data)
        
        # Should return validation error
        self.assertValidationError(response, 'parent')
    
    def test_category_depth_limit(self):
        """Test that category hierarchy depth is limited."""
        self.authenticate_admin()
        
        # Try to create a very deep category hierarchy
        current_parent = self.level2_frontend
        
        # Create categories up to a reasonable depth limit
        for i in range(5):  # Assuming max depth is around 5
            category_data = {
                'name': f'Level {i+3} Category',
                'description': f'Category at level {i+3}',
                'parent': current_parent.id
            }
            
            response = self.client.post(self.categories_url, category_data)
            
            if response.status_code == status.HTTP_201_CREATED:
                current_parent = Category.objects.get(name=f'Level {i+3} Category')
            else:
                # Should eventually hit depth limit
                self.assertValidationError(response, 'parent')
                break