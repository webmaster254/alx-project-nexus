"""
Factory classes for generating test data using factory_boy.
Provides consistent test data generation for all models.
"""
import factory
from factory.django import DjangoModelFactory
from factory import fuzzy
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from apps.authentication.models import UserProfile
from apps.categories.models import Industry, JobType, Category
from apps.jobs.models import Company, Job
from apps.applications.models import ApplicationStatus, Application, Document

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_admin = False
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')


class AdminUserFactory(UserFactory):
    """Factory for creating admin User instances."""
    
    username = factory.Sequence(lambda n: f"admin{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    is_admin = True
    is_staff = True
    is_superuser = True


class UserProfileFactory(DjangoModelFactory):
    """Factory for creating UserProfile instances."""
    
    class Meta:
        model = UserProfile
    
    user = factory.SubFactory(UserFactory)
    phone_number = factory.Faker('phone_number')
    bio = factory.Faker('text', max_nb_chars=400)
    location = factory.Faker('city')
    website = factory.Faker('url')
    linkedin_url = factory.LazyAttribute(
        lambda obj: f"https://linkedin.com/in/{obj.user.username}"
    )
    github_url = factory.LazyAttribute(
        lambda obj: f"https://github.com/{obj.user.username}"
    )
    skills = factory.LazyFunction(
        lambda: ', '.join(random.sample([
            'Python', 'JavaScript', 'React', 'Django', 'PostgreSQL',
            'Docker', 'AWS', 'Git', 'HTML', 'CSS', 'Node.js', 'Vue.js'
        ], k=random.randint(3, 8)))
    )
    experience_years = fuzzy.FuzzyInteger(0, 20)


class IndustryFactory(DjangoModelFactory):
    """Factory for creating Industry instances."""
    
    class Meta:
        model = Industry
        django_get_or_create = ('name',)
    
    name = factory.Iterator([
        'Technology', 'Healthcare', 'Finance', 'Education', 'Manufacturing',
        'Retail', 'Consulting', 'Media', 'Transportation', 'Real Estate'
    ])
    description = factory.Faker('text', max_nb_chars=200)
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    is_active = True


class JobTypeFactory(DjangoModelFactory):
    """Factory for creating JobType instances."""
    
    class Meta:
        model = JobType
        django_get_or_create = ('name',)
    
    name = factory.Iterator([
        'Full-time', 'Part-time', 'Contract', 'Temporary', 
        'Internship', 'Freelance', 'Remote', 'Hybrid'
    ])
    code = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    description = factory.Faker('text', max_nb_chars=150)
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    is_active = True


class CategoryFactory(DjangoModelFactory):
    """Factory for creating Category instances."""
    
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f'Category {n}')
    description = factory.Faker('text', max_nb_chars=200)
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    parent = None
    is_active = True


class SubCategoryFactory(CategoryFactory):
    """Factory for creating sub-categories with parent relationships."""
    
    parent = factory.SubFactory(CategoryFactory)
    name = factory.Iterator([
        'Frontend Development', 'Backend Development', 'Mobile Development',
        'DevOps', 'QA Testing', 'UI/UX Design', 'Graphic Design',
        'Digital Marketing', 'Content Marketing', 'SEO'
    ])


class CompanyFactory(DjangoModelFactory):
    """Factory for creating Company instances."""
    
    class Meta:
        model = Company
    
    name = factory.Faker('company')
    description = factory.Faker('text', max_nb_chars=500)
    website = factory.Faker('url')
    email = factory.Faker('company_email')
    phone = factory.Faker('phone_number')
    address = factory.Faker('address')
    founded_year = fuzzy.FuzzyInteger(1950, 2020)
    employee_count = factory.Iterator([
        '1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'
    ])
    slug = factory.LazyAttribute(
        lambda obj: obj.name.lower().replace(' ', '-').replace(',', '').replace('.', '')
    )
    is_active = True


class JobFactory(DjangoModelFactory):
    """Factory for creating Job instances."""
    
    class Meta:
        model = Job
    
    title = factory.Iterator([
        'Senior Software Engineer', 'Product Manager', 'Data Scientist',
        'UX Designer', 'Marketing Manager', 'Sales Representative',
        'DevOps Engineer', 'Frontend Developer', 'Backend Developer',
        'Full Stack Developer', 'Mobile Developer', 'QA Engineer'
    ])
    description = factory.Faker('text', max_nb_chars=1000)
    summary = factory.Faker('text', max_nb_chars=300)
    company = factory.SubFactory(CompanyFactory)
    location = factory.Faker('city')
    is_remote = factory.Faker('boolean', chance_of_getting_true=30)
    salary_min = fuzzy.FuzzyDecimal(40000, 80000, 2)
    salary_max = factory.LazyAttribute(
        lambda obj: obj.salary_min + fuzzy.FuzzyDecimal(10000, 50000, 2).fuzz()
    )
    salary_type = factory.Iterator(['hourly', 'monthly', 'yearly'])
    salary_currency = 'USD'
    job_type = factory.SubFactory(JobTypeFactory)
    industry = factory.SubFactory(IndustryFactory)
    experience_level = factory.Iterator([
        'entry', 'junior', 'mid', 'senior', 'lead', 'executive'
    ])
    required_skills = factory.LazyFunction(
        lambda: ', '.join(random.sample([
            'Python', 'JavaScript', 'React', 'Django', 'PostgreSQL',
            'Docker', 'AWS', 'Git', 'HTML', 'CSS', 'Node.js', 'Vue.js',
            'TypeScript', 'MongoDB', 'Redis', 'Kubernetes'
        ], k=random.randint(3, 6)))
    )
    preferred_skills = factory.LazyFunction(
        lambda: ', '.join(random.sample([
            'GraphQL', 'Microservices', 'CI/CD', 'Terraform', 'Ansible',
            'Machine Learning', 'Data Analysis', 'Agile', 'Scrum'
        ], k=random.randint(2, 4)))
    )
    application_deadline = factory.LazyFunction(
        lambda: timezone.now() + timedelta(days=random.randint(7, 60))
    )
    is_active = True
    is_featured = factory.Faker('boolean', chance_of_getting_true=20)
    views_count = fuzzy.FuzzyInteger(0, 1000)
    applications_count = fuzzy.FuzzyInteger(0, 50)
    created_by = factory.SubFactory(AdminUserFactory)
    updated_by = factory.SelfAttribute('created_by')
    
    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        """Add categories to the job after creation."""
        if not create:
            return
        
        if extracted:
            for category in extracted:
                self.categories.add(category)
        else:
            # Add 1-3 random categories
            categories = CategoryFactory.create_batch(random.randint(1, 3))
            for category in categories:
                self.categories.add(category)


class RemoteJobFactory(JobFactory):
    """Factory for creating remote Job instances."""
    
    location = 'Remote'
    is_remote = True


class FeaturedJobFactory(JobFactory):
    """Factory for creating featured Job instances."""
    
    is_featured = True
    views_count = fuzzy.FuzzyInteger(500, 2000)
    applications_count = fuzzy.FuzzyInteger(20, 100)


class ApplicationStatusFactory(DjangoModelFactory):
    """Factory for creating ApplicationStatus instances."""
    
    class Meta:
        model = ApplicationStatus
        django_get_or_create = ('name',)
    
    name = factory.Iterator(['pending', 'reviewed', 'accepted', 'rejected', 'withdrawn'])
    display_name = factory.LazyAttribute(lambda obj: {
        'pending': 'Pending Review',
        'reviewed': 'Under Review',
        'accepted': 'Accepted',
        'rejected': 'Rejected',
        'withdrawn': 'Withdrawn'
    }[obj.name])
    description = factory.LazyAttribute(lambda obj: {
        'pending': 'Application has been submitted and is awaiting review',
        'reviewed': 'Application is currently under review',
        'accepted': 'Application has been accepted',
        'rejected': 'Application has been rejected',
        'withdrawn': 'Application was withdrawn by the applicant'
    }[obj.name])
    is_final = factory.LazyAttribute(lambda obj: obj.name in ['accepted', 'rejected', 'withdrawn'])


class ApplicationFactory(DjangoModelFactory):
    """Factory for creating Application instances."""
    
    class Meta:
        model = Application
    
    user = factory.SubFactory(UserFactory)
    job = factory.SubFactory(JobFactory)
    status = factory.SubFactory(ApplicationStatusFactory, name='pending')
    cover_letter = factory.Faker('text', max_nb_chars=800)
    notes = factory.Faker('text', max_nb_chars=200)
    reviewed_by = None
    reviewed_at = None


class ReviewedApplicationFactory(ApplicationFactory):
    """Factory for creating reviewed Application instances."""
    
    status = factory.SubFactory(ApplicationStatusFactory, name='reviewed')
    reviewed_by = factory.SubFactory(AdminUserFactory)
    reviewed_at = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=random.randint(1, 7))
    )


class AcceptedApplicationFactory(ApplicationFactory):
    """Factory for creating accepted Application instances."""
    
    status = factory.SubFactory(ApplicationStatusFactory, name='accepted')
    reviewed_by = factory.SubFactory(AdminUserFactory)
    reviewed_at = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=random.randint(1, 14))
    )


class RejectedApplicationFactory(ApplicationFactory):
    """Factory for creating rejected Application instances."""
    
    status = factory.SubFactory(ApplicationStatusFactory, name='rejected')
    reviewed_by = factory.SubFactory(AdminUserFactory)
    reviewed_at = factory.LazyFunction(
        lambda: timezone.now() - timedelta(days=random.randint(1, 14))
    )


class DocumentFactory(DjangoModelFactory):
    """Factory for creating Document instances."""
    
    class Meta:
        model = Document
    
    application = factory.SubFactory(ApplicationFactory)
    document_type = factory.Iterator(['resume', 'cover_letter', 'portfolio', 'certificate', 'other'])
    title = factory.LazyAttribute(lambda obj: {
        'resume': f"{obj.application.user.get_full_name()} - Resume",
        'cover_letter': f"{obj.application.user.get_full_name()} - Cover Letter",
        'portfolio': f"{obj.application.user.get_full_name()} - Portfolio",
        'certificate': f"{obj.application.user.get_full_name()} - Certificate",
        'other': f"{obj.application.user.get_full_name()} - Document"
    }[obj.document_type])
    file = factory.django.FileField(filename='test_document.pdf')
    file_size = fuzzy.FuzzyInteger(1024, 5242880)  # 1KB to 5MB
    content_type = factory.LazyAttribute(lambda obj: {
        'resume': 'application/pdf',
        'cover_letter': 'application/pdf',
        'portfolio': 'application/pdf',
        'certificate': 'application/pdf',
        'other': 'application/pdf'
    }[obj.document_type])
    description = factory.Faker('text', max_nb_chars=200)


class ResumeDocumentFactory(DocumentFactory):
    """Factory for creating resume Document instances."""
    
    document_type = 'resume'
    title = factory.LazyAttribute(lambda obj: f"{obj.application.user.get_full_name()} - Resume")
    content_type = 'application/pdf'


# Utility functions for creating test data sets

def create_complete_user_with_profile():
    """Create a user with a complete profile."""
    user = UserFactory()
    profile = UserProfileFactory(user=user)
    return user, profile


def create_job_with_applications(num_applications=5):
    """Create a job with multiple applications."""
    job = JobFactory()
    applications = []
    
    for _ in range(num_applications):
        user = UserFactory()
        application = ApplicationFactory(user=user, job=job)
        applications.append(application)
    
    return job, applications


def create_category_hierarchy():
    """Create a hierarchical category structure."""
    # Root categories
    tech_category = CategoryFactory(name='Technology')
    business_category = CategoryFactory(name='Business')
    
    # Sub-categories
    dev_category = SubCategoryFactory(name='Software Development', parent=tech_category)
    design_category = SubCategoryFactory(name='Design', parent=tech_category)
    marketing_category = SubCategoryFactory(name='Marketing', parent=business_category)
    sales_category = SubCategoryFactory(name='Sales', parent=business_category)
    
    # Sub-sub-categories
    frontend_category = SubCategoryFactory(name='Frontend Development', parent=dev_category)
    backend_category = SubCategoryFactory(name='Backend Development', parent=dev_category)
    
    return {
        'root': [tech_category, business_category],
        'level1': [dev_category, design_category, marketing_category, sales_category],
        'level2': [frontend_category, backend_category]
    }


def create_company_with_jobs(num_jobs=3):
    """Create a company with multiple job postings."""
    company = CompanyFactory()
    jobs = []
    
    for _ in range(num_jobs):
        job = JobFactory(company=company)
        jobs.append(job)
    
    return company, jobs


def create_application_with_documents():
    """Create an application with associated documents."""
    application = ApplicationFactory()
    
    # Create resume and cover letter documents
    resume = ResumeDocumentFactory(application=application)
    cover_letter = DocumentFactory(
        application=application,
        document_type='cover_letter',
        title=f"{application.user.get_full_name()} - Cover Letter"
    )
    
    return application, [resume, cover_letter]