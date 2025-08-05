# Job Board Backend API

A Django REST Framework-based backend API for a job board application.

## Project Structure

```
job_board_backend/
├── config/                 # Django project configuration
│   ├── settings/           # Modular settings (base, development, production)
│   ├── urls.py            # Main URL configuration
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
├── apps/                   # Django applications
│   ├── authentication/    # User authentication and management
│   ├── jobs/              # Job posting management
│   ├── applications/      # Job application management
│   ├── categories/        # Job categorization system
│   └── common/            # Shared utilities and models
├── requirements/          # Python dependencies
│   ├── base.txt          # Base requirements
│   └── development.txt   # Development requirements
├── logs/                  # Application logs
├── media/                 # User uploaded files
├── static/               # Static files
└── templates/            # Django templates
```

## Setup Instructions

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements/development.txt
   ```

3. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your database and other settings
   ```

4. **Database setup:**
   ```bash
   # Make sure PostgreSQL is running
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## API Documentation

Once the server is running, you can access:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

## Technology Stack

- **Framework:** Django 4.2+ with Django REST Framework
- **Database:** PostgreSQL 14+
- **Authentication:** JWT using djangorestframework-simplejwt
- **Documentation:** drf-spectacular for OpenAPI/Swagger
- **Testing:** pytest-django with factory-boy

## Development

The project uses modular settings:
- `config.settings.development` - Development settings (default for manage.py)
- `config.settings.production` - Production settings (used by WSGI/ASGI)
- `config.settings.base` - Base settings shared by all environments

## Next Steps

This is the basic project structure. The following tasks will implement:
1. Custom user authentication system
2. Job posting management
3. Job application system
4. Category management
5. Search and filtering
6. API documentation
7. Testing suite
8. Production deployment configuration