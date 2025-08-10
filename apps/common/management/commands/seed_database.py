"""
Management command to seed the database with test data.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
import random

from tests.factories import (
    UserFactory, AdminUserFactory, UserProfileFactory,
    IndustryFactory, JobTypeFactory, CategoryFactory, SubCategoryFactory,
    CompanyFactory, JobFactory, RemoteJobFactory, FeaturedJobFactory,
    ApplicationStatusFactory, ApplicationFactory, ReviewedApplicationFactory,
    AcceptedApplicationFactory, RejectedApplicationFactory,
    DocumentFactory, ResumeDocumentFactory,
    create_complete_user_with_profile,
    create_job_with_applications,
    create_category_hierarchy,
    create_company_with_jobs,
    create_application_with_documents
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed the database with test data for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of regular users to create (default: 20)'
        )
        parser.add_argument(
            '--companies',
            type=int,
            default=15,
            help='Number of companies to create (default: 15)'
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=50,
            help='Number of jobs to create (default: 50)'
        )
        parser.add_argument(
            '--applications',
            type=int,
            default=100,
            help='Number of applications to create (default: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
        parser.add_argument(
            '--minimal',
            action='store_true',
            help='Create minimal test data (faster for quick testing)'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(
                self.style.WARNING('Clearing existing data...')
            )
            self.clear_data()

        if options['minimal']:
            self.stdout.write(
                self.style.SUCCESS('Creating minimal test data...')
            )
            self.create_minimal_data()
        else:
            self.stdout.write(
                self.style.SUCCESS('Seeding database with test data...')
            )
            self.create_full_data(options)

        self.stdout.write(
            self.style.SUCCESS('Database seeding completed successfully!')
        )

    def clear_data(self):
        """Clear existing test data (keep superusers)."""
        from apps.applications.models import Application, ApplicationStatus, Document
        from apps.jobs.models import Job, Company
        from apps.categories.models import Category, Industry, JobType
        from apps.authentication.models import UserProfile

        with transaction.atomic():
            # Clear in reverse dependency order
            Document.objects.all().delete()
            Application.objects.all().delete()
            Job.objects.all().delete()
            Company.objects.all().delete()
            Category.objects.all().delete()
            Industry.objects.all().delete()
            JobType.objects.all().delete()
            ApplicationStatus.objects.all().delete()
            
            # Clear users but keep superusers
            User.objects.filter(is_superuser=False).delete()
            UserProfile.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS('Existing data cleared.')
        )

    def create_minimal_data(self):
        """Create minimal test data for quick testing."""
        with transaction.atomic():
            # Create application statuses
            self.create_application_statuses()
            
            # Create basic classification data
            tech_industry = IndustryFactory(name='Technology')
            healthcare_industry = IndustryFactory(name='Healthcare')
            
            fulltime_type = JobTypeFactory(name='Full-time', code='full-time')
            parttime_type = JobTypeFactory(name='Part-time', code='part-time')
            
            # Create simple category structure
            categories = create_category_hierarchy()
            
            # Create admin user
            admin = AdminUserFactory(
                username='admin',
                email='admin@jobboard.com',
                first_name='Admin',
                last_name='User'
            )
            
            # Create a few regular users
            users = UserFactory.create_batch(5)
            for user in users[:3]:
                UserProfileFactory(user=user)
            
            # Create a few companies
            companies = CompanyFactory.create_batch(3)
            
            # Create some jobs
            jobs = []
            for i, company in enumerate(companies):
                job = JobFactory(
                    company=company,
                    industry=tech_industry if i % 2 == 0 else healthcare_industry,
                    job_type=fulltime_type if i % 2 == 0 else parttime_type,
                    created_by=admin
                )
                job.categories.add(categories['level1'][i % len(categories['level1'])])
                jobs.append(job)
            
            # Create some applications
            for user in users:
                for job in jobs[:2]:  # Each user applies to first 2 jobs
                    ApplicationFactory(user=user, job=job)

        self.stdout.write(
            self.style.SUCCESS('Minimal test data created:')
        )
        self.stdout.write(f'  - 1 admin user (admin@jobboard.com / testpass123)')
        self.stdout.write(f'  - 5 regular users')
        self.stdout.write(f'  - 3 companies')
        self.stdout.write(f'  - 3 jobs')
        self.stdout.write(f'  - 10 applications')

    def create_full_data(self, options):
        """Create comprehensive test data."""
        num_users = options['users']
        num_companies = options['companies']
        num_jobs = options['jobs']
        num_applications = options['applications']

        with transaction.atomic():
            # Create application statuses
            self.create_application_statuses()
            
            # Create industries
            industries = self.create_industries()
            
            # Create job types
            job_types = self.create_job_types()
            
            # Create category hierarchy
            categories = create_category_hierarchy()
            
            # Create admin users
            admin = AdminUserFactory(
                username='admin',
                email='admin@jobboard.com',
                first_name='Admin',
                last_name='User'
            )
            
            hr_admin = AdminUserFactory(
                username='hradmin',
                email='hr@jobboard.com',
                first_name='HR',
                last_name='Admin'
            )
            
            # Create regular users with profiles
            self.stdout.write('Creating users...')
            users = []
            for i in range(num_users):
                user, profile = create_complete_user_with_profile()
                users.append(user)
                if i % 10 == 0:
                    self.stdout.write(f'  Created {i + 1}/{num_users} users')
            
            # Create companies
            self.stdout.write('Creating companies...')
            companies = CompanyFactory.create_batch(num_companies)
            
            # Create jobs
            self.stdout.write('Creating jobs...')
            jobs = []
            for i in range(num_jobs):
                # Mix of different job types
                if i % 10 == 0:
                    job = RemoteJobFactory(
                        company=random.choice(companies),
                        industry=random.choice(industries),
                        job_type=random.choice(job_types),
                        created_by=random.choice([admin, hr_admin])
                    )
                elif i % 15 == 0:
                    job = FeaturedJobFactory(
                        company=random.choice(companies),
                        industry=random.choice(industries),
                        job_type=random.choice(job_types),
                        created_by=random.choice([admin, hr_admin])
                    )
                else:
                    job = JobFactory(
                        company=random.choice(companies),
                        industry=random.choice(industries),
                        job_type=random.choice(job_types),
                        created_by=random.choice([admin, hr_admin])
                    )
                
                # Add random categories
                available_categories = categories['level1'] + categories['level2']
                job_categories = random.sample(
                    available_categories, 
                    random.randint(1, 3)
                )
                for category in job_categories:
                    job.categories.add(category)
                
                jobs.append(job)
                
                if i % 10 == 0:
                    self.stdout.write(f'  Created {i + 1}/{num_jobs} jobs')
            
            # Create applications
            self.stdout.write('Creating applications...')
            applications = []
            for i in range(num_applications):
                user = random.choice(users)
                job = random.choice(jobs)
                
                # Check if user already applied to this job
                existing = any(
                    app.user == user and app.job == job 
                    for app in applications
                )
                if existing:
                    continue
                
                # Create different types of applications
                app_type = random.randint(1, 10)
                if app_type <= 5:  # 50% pending
                    application = ApplicationFactory(user=user, job=job)
                elif app_type <= 7:  # 20% reviewed
                    application = ReviewedApplicationFactory(
                        user=user, 
                        job=job,
                        reviewed_by=random.choice([admin, hr_admin])
                    )
                elif app_type <= 8:  # 10% accepted
                    application = AcceptedApplicationFactory(
                        user=user, 
                        job=job,
                        reviewed_by=random.choice([admin, hr_admin])
                    )
                else:  # 20% rejected
                    application = RejectedApplicationFactory(
                        user=user, 
                        job=job,
                        reviewed_by=random.choice([admin, hr_admin])
                    )
                
                applications.append(application)
                
                # Add documents to some applications
                if random.random() < 0.7:  # 70% have resume
                    ResumeDocumentFactory(application=application)
                
                if random.random() < 0.3:  # 30% have additional documents
                    DocumentFactory(
                        application=application,
                        document_type=random.choice(['portfolio', 'certificate', 'other'])
                    )
                
                if i % 20 == 0:
                    self.stdout.write(f'  Created {i + 1}/{num_applications} applications')

        # Print summary
        self.stdout.write(
            self.style.SUCCESS('\nDatabase seeded successfully!')
        )
        self.stdout.write(f'Created:')
        self.stdout.write(f'  - 2 admin users (admin@jobboard.com, hr@jobboard.com)')
        self.stdout.write(f'  - {num_users} regular users')
        self.stdout.write(f'  - {len(industries)} industries')
        self.stdout.write(f'  - {len(job_types)} job types')
        self.stdout.write(f'  - {len(categories["root"]) + len(categories["level1"]) + len(categories["level2"])} categories')
        self.stdout.write(f'  - {num_companies} companies')
        self.stdout.write(f'  - {num_jobs} jobs')
        self.stdout.write(f'  - {len(applications)} applications')
        self.stdout.write(f'\nLogin credentials:')
        self.stdout.write(f'  Admin: admin@jobboard.com / testpass123')
        self.stdout.write(f'  HR Admin: hr@jobboard.com / testpass123')

    def create_application_statuses(self):
        """Create application status records."""
        statuses = [
            ('pending', 'Pending Review', 'Application has been submitted and is awaiting review', False),
            ('reviewed', 'Under Review', 'Application is currently under review', False),
            ('accepted', 'Accepted', 'Application has been accepted', True),
            ('rejected', 'Rejected', 'Application has been rejected', True),
            ('withdrawn', 'Withdrawn', 'Application was withdrawn by the applicant', True),
        ]
        
        for name, display_name, description, is_final in statuses:
            ApplicationStatusFactory(
                name=name,
                display_name=display_name,
                description=description,
                is_final=is_final
            )

    def create_industries(self):
        """Create industry records."""
        industry_names = [
            'Technology', 'Healthcare', 'Finance', 'Education',
            'Manufacturing', 'Retail', 'Consulting', 'Media',
            'Transportation', 'Real Estate', 'Government',
            'Non-profit', 'Energy', 'Telecommunications'
        ]
        
        industries = []
        for name in industry_names:
            industry = IndustryFactory(name=name)
            industries.append(industry)
        
        return industries

    def create_job_types(self):
        """Create job type records."""
        job_type_data = [
            ('Full-time', 'full-time'),
            ('Part-time', 'part-time'),
            ('Contract', 'contract'),
            ('Temporary', 'temporary'),
            ('Internship', 'internship'),
            ('Freelance', 'freelance'),
            ('Remote', 'remote'),
            ('Hybrid', 'hybrid'),
        ]
        
        job_types = []
        for name, code in job_type_data:
            job_type = JobTypeFactory(name=name, code=code)
            job_types.append(job_type)
        
        return job_types