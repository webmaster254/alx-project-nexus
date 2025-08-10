# Job Board Backend Database - Entity Relationship Diagram

## Database Schema Overview

This ERD represents the complete database structure for the Job Board Backend application, showing all entities, their attributes, and relationships.

```mermaid
erDiagram
    %% User Authentication & Profile
    User {
        int id PK
        string username
        string email UK "Unique, used for authentication"
        string first_name
        string last_name
        string password
        boolean is_staff
        boolean is_active
        boolean is_superuser
        boolean is_admin "Custom admin flag"
        datetime date_joined
        datetime last_login
        datetime created_at
        datetime updated_at
    }

    UserProfile {
        int id PK
        int user_id FK "OneToOne with User"
        string phone_number "Max 17 chars"
        text bio "Max 500 chars"
        string location "Max 100 chars"
        string website
        string linkedin_url
        string github_url
        file resume "Upload path: resumes/"
        text skills "Comma-separated"
        int experience_years
        datetime created_at
        datetime updated_at
    }

    %% Company Management
    Company {
        int id PK
        string name UK "Max 200 chars, unique"
        text description
        string website
        string email
        string phone "Max 20 chars"
        text address
        file logo "Upload path: company_logos/"
        int founded_year
        string employee_count "Max 50 chars"
        string slug UK "Max 220 chars, unique"
        boolean is_active
        tsvector search_vector "Full-text search"
        datetime created_at
        datetime updated_at
    }

    %% Job Classification
    Industry {
        int id PK
        string name UK "Max 100 chars, unique"
        text description
        string slug UK "Max 120 chars, unique"
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    JobType {
        int id PK
        string name UK "Max 50 chars, unique"
        string code UK "Max 20 chars, unique"
        text description
        string slug UK "Max 70 chars, unique"
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Category {
        int id PK
        string name "Max 100 chars"
        text description
        string slug UK "Max 120 chars, unique"
        int parent_id FK "Self-referencing for hierarchy"
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    %% Job Management
    Job {
        int id PK
        string title "Max 200 chars"
        text description
        text summary "Max 500 chars"
        int company_id FK
        string location "Max 200 chars"
        boolean is_remote
        decimal salary_min "10 digits, 2 decimal places"
        decimal salary_max "10 digits, 2 decimal places"
        string salary_type "hourly/monthly/yearly"
        string salary_currency "3 chars, default USD"
        int job_type_id FK
        int industry_id FK
        string experience_level "entry/junior/mid/senior/lead/executive"
        text required_skills "Comma-separated"
        text preferred_skills "Comma-separated"
        datetime application_deadline
        string external_url
        boolean is_active
        boolean is_featured
        int views_count "Default 0"
        int applications_count "Default 0"
        int created_by_id FK
        int updated_by_id FK
        tsvector search_vector "Full-text search"
        datetime created_at
        datetime updated_at
    }

    JobCategories {
        int id PK
        int job_id FK
        int category_id FK
    }

    %% Application Management
    ApplicationStatus {
        int id PK
        string name UK "Max 20 chars, unique"
        string display_name "Max 50 chars"
        text description
        boolean is_final "Whether status is final"
        datetime created_at
        datetime updated_at
    }

    Application {
        int id PK
        int user_id FK
        int job_id FK
        int status_id FK
        text cover_letter
        text notes "Internal admin notes"
        datetime applied_at
        datetime updated_at
        datetime reviewed_at
        int reviewed_by_id FK
    }

    Document {
        int id PK
        int application_id FK
        string document_type "resume/cover_letter/portfolio/certificate/other"
        string title "Max 200 chars"
        file file "Upload path: application_documents/"
        int file_size "Bytes"
        string content_type "MIME type, max 100 chars"
        text description
        datetime uploaded_at
    }

    %% Relationships
    User ||--o| UserProfile : "has profile"
    User ||--o{ Job : "creates jobs"
    User ||--o{ Job : "updates jobs"
    User ||--o{ Application : "submits applications"
    User ||--o{ Application : "reviews applications"

    Company ||--o{ Job : "posts jobs"
    
    Industry ||--o{ Job : "categorizes jobs"
    JobType ||--o{ Job : "defines employment type"
    Category ||--o{ Category : "parent-child hierarchy"
    
    Job }o--o{ Category : "belongs to categories"
    Job ||--o{ Application : "receives applications"
    
    ApplicationStatus ||--o{ Application : "defines status"
    Application ||--o{ Document : "includes documents"

    %% Indexes and Constraints
    %% User: email is unique and used for authentication
    %% Company: name and slug are unique
    %% Industry: name and slug are unique  
    %% JobType: name, code, and slug are unique
    %% Category: slug is unique, name+parent is unique together
    %% Job: Multiple indexes on title, location, is_active, created_at, company+is_active, industry+job_type, location+is_active
    %% Application: user+job is unique together, indexes on user+status, job+status, applied_at, status+applied_at
    %% ApplicationStatus: name is unique
    %% Document: indexes on application+document_type, uploaded_at
```

## Key Database Features

### 1. **User Management**
- **User**: Extended Django's AbstractUser with email authentication
- **UserProfile**: One-to-one relationship with User for additional profile data
- Supports both regular users and admin users

### 2. **Company & Job Management**
- **Company**: Stores employer information with full-text search capability
- **Job**: Comprehensive job posting model with salary ranges, skills, and metadata
- **Many-to-Many**: Jobs can belong to multiple categories

### 3. **Hierarchical Classification**
- **Industry**: Flat structure for industry classification
- **JobType**: Employment type classification (full-time, part-time, etc.)
- **Category**: Hierarchical structure supporting up to 3 levels deep

### 4. **Application Workflow**
- **ApplicationStatus**: Configurable status types (pending, reviewed, accepted, etc.)
- **Application**: Links users to jobs with status tracking
- **Document**: File attachments for applications (resumes, portfolios, etc.)

### 5. **Search & Performance**
- Full-text search vectors on Company and Job models
- Strategic database indexes for common query patterns
- Optimized for filtering by location, industry, job type, and status

### 6. **Data Integrity**
- Unique constraints prevent duplicate applications
- Foreign key relationships maintain referential integrity
- Validation prevents circular references in category hierarchy
- Soft deletes through is_active flags

### 7. **Audit Trail**
- Created/updated timestamps on all major entities
- User tracking for job creation and updates
- Application review tracking with reviewer information

## Database Tables Summary

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `auth_user` | User authentication | Email-based login, admin flags |
| `user_profile` | Extended user data | Skills, experience, contact info |
| `company` | Employer information | Full-text search, slug URLs |
| `industry` | Industry classification | Flat structure, active/inactive |
| `job_type` | Employment types | Standardized codes |
| `category` | Job categories | Hierarchical, max 3 levels |
| `job` | Job postings | Rich metadata, search vectors |
| `job_categories` | Job-Category mapping | Many-to-many relationship |
| `application_status` | Status definitions | Configurable workflow states |
| `application` | Job applications | User-job linking, status tracking |
| `application_document` | File attachments | Resume, portfolio uploads |

## Relationships Summary

- **One-to-One**: User ↔ UserProfile
- **One-to-Many**: Company → Jobs, Industry → Jobs, JobType → Jobs, User → Applications, Job → Applications
- **Many-to-Many**: Job ↔ Categories
- **Self-Referencing**: Category → Category (parent-child)
- **Polymorphic**: User can be both job creator and applicant

This ERD provides a comprehensive view of the job board database structure, supporting all major features including job posting, application management, user profiles, and hierarchical categorization.