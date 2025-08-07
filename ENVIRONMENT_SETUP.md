# Environment Setup Guide

This guide covers setting up the Job Board Backend API in different environments.

## Table of Contents

1. [Development Environment](#development-environment)
2. [Staging Environment](#staging-environment)
3. [Production Environment](#production-environment)
4. [Docker Environment](#docker-environment)
5. [Environment Variables Reference](#environment-variables-reference)
6. [Database Setup](#database-setup)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring Setup](#monitoring-setup)

## Development Environment

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd job-board-backend
   ```

2. **Create virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with development settings
   ```

5. **Set up database:**
   ```bash
   # Create database
   createdb job_board_dev
   
   # Run migrations
   python manage.py migrate --settings=config.settings.development
   
   # Create superuser
   python manage.py createsuperuser --settings=config.settings.development
   ```

6. **Run development server:**
   ```bash
   python manage.py runserver --settings=config.settings.development
   ```

### Development Environment Variables

```bash
# .env for development
SECRET_KEY=dev-secret-key-not-for-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/job_board_dev

# Development settings
LOG_LEVEL=DEBUG
ENABLE_PERFORMANCE_MONITORING=True
```

## Staging Environment

### Prerequisites

- Production-like server environment
- PostgreSQL 14+
- Nginx (optional)
- SSL certificates (recommended)

### Setup Steps

1. **Server preparation:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install python3.11 python3.11-venv postgresql-client nginx git
   
   # Create application user
   sudo useradd -m -s /bin/bash jobboard-staging
   sudo su - jobboard-staging
   ```

2. **Application setup:**
   ```bash
   # Clone repository
   git clone <repository-url> app
   cd app
   
   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements/production.txt
   ```

3. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with staging settings
   ```

4. **Database setup:**
   ```bash
   # Run migrations
   python scripts/migrate.py --settings=config.settings.production
   
   # Create superuser
   python manage.py createsuperuser --settings=config.settings.production
   ```

5. **Deploy and test:**
   ```bash
   python scripts/deploy.py
   python scripts/test_deployment.py --url http://staging.yourdomain.com
   ```

### Staging Environment Variables

```bash
# .env for staging
SECRET_KEY=staging-secret-key-different-from-production
DEBUG=False
ALLOWED_HOSTS=staging.yourdomain.com

# Database
DATABASE_URL=postgresql://staging_user:staging_password@db-host:5432/job_board_staging

# Security (less strict than production)
SECURE_SSL_REDIRECT=False  # Enable when SSL is configured
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Logging
LOG_DIR=/var/log/django-staging
LOG_LEVEL=INFO
```

## Production Environment

### Prerequisites

- Production server (Ubuntu 20.04+ recommended)
- PostgreSQL 14+ (managed service recommended)
- Redis (for caching)
- Nginx (reverse proxy)
- SSL certificates
- Monitoring tools

### Setup Steps

1. **Server hardening:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install fail2ban
   sudo apt install fail2ban
   
   # Configure firewall
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```

2. **Install dependencies:**
   ```bash
   sudo apt install python3.11 python3.11-venv postgresql-client redis-tools nginx certbot python3-certbot-nginx
   ```

3. **Create application user:**
   ```bash
   sudo useradd -m -s /bin/bash jobboard
   sudo mkdir -p /var/log/django /var/www/static /var/www/media
   sudo chown -R jobboard:jobboard /var/log/django /var/www/static /var/www/media
   ```

4. **Application deployment:**
   ```bash
   sudo su - jobboard
   git clone <repository-url> app
   cd app
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements/production.txt
   ```

5. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Configure production environment variables
   ```

6. **SSL certificate setup:**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
   ```

7. **Deploy application:**
   ```bash
   python scripts/validate_deployment.py
   python scripts/deploy.py
   ```

8. **Set up systemd service:**
   ```bash
   sudo cp deployment/jobboard.service /etc/systemd/system/
   sudo systemctl enable jobboard
   sudo systemctl start jobboard
   ```

9. **Configure nginx:**
   ```bash
   sudo cp nginx/nginx.conf /etc/nginx/sites-available/jobboard
   sudo ln -s /etc/nginx/sites-available/jobboard /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

10. **Final testing:**
    ```bash
    python scripts/test_deployment.py --url https://api.yourdomain.com
    ```

### Production Environment Variables

```bash
# .env for production
SECRET_KEY=super-secure-production-secret-key-50-chars-minimum
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Database (use managed service)
DATABASE_URL=postgresql://prod_user:secure_password@prod-db-host:5432/job_board_prod

# Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Caching
REDIS_URL=redis://redis-host:6379/1

# Logging
LOG_DIR=/var/log/django
LOG_LEVEL=INFO
ENABLE_STRUCTURED_LOGGING=True

# Performance
ENABLE_PERFORMANCE_MONITORING=True
SLOW_QUERY_THRESHOLD=1.0

# Email
EMAIL_HOST=smtp.yourdomain.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=secure_email_password
```

## Docker Environment

### Development with Docker

1. **Start development environment:**
   ```bash
   docker-compose up -d
   ```

2. **Run management commands:**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f web
   ```

### Production with Docker

1. **Build and deploy:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

2. **Scale services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --scale web=3
   ```

3. **Monitor services:**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   docker-compose -f docker-compose.prod.yml logs web
   ```

## Environment Variables Reference

### Core Django Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Django secret key (50+ chars) |
| `DEBUG` | No | False | Debug mode (never True in production) |
| `ALLOWED_HOSTS` | Yes | - | Comma-separated list of allowed hosts |
| `TIME_ZONE` | No | UTC | Application timezone |
| `LANGUAGE_CODE` | No | en-us | Default language |

### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes* | - | Complete database URL |
| `DB_NAME` | Yes* | - | Database name |
| `DB_USER` | Yes* | - | Database user |
| `DB_PASSWORD` | Yes* | - | Database password |
| `DB_HOST` | Yes* | localhost | Database host |
| `DB_PORT` | No | 5432 | Database port |

*Either `DATABASE_URL` or individual `DB_*` variables required

### Security Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECURE_SSL_REDIRECT` | No | False | Redirect HTTP to HTTPS |
| `SESSION_COOKIE_SECURE` | No | False | Secure session cookies |
| `CSRF_COOKIE_SECURE` | No | False | Secure CSRF cookies |
| `CSRF_TRUSTED_ORIGINS` | No | - | Trusted origins for CSRF |

### Caching Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDIS_URL` | No | - | Redis connection URL |
| `CACHE_TIMEOUT` | No | 300 | Default cache timeout |

### Logging Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_DIR` | No | /var/log/django | Log directory |
| `LOG_LEVEL` | No | INFO | Logging level |
| `LOG_MAX_BYTES` | No | 52428800 | Max log file size |
| `LOG_BACKUP_COUNT` | No | 10 | Number of backup files |

### Email Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMAIL_HOST` | No | - | SMTP server host |
| `EMAIL_PORT` | No | 587 | SMTP server port |
| `EMAIL_USE_TLS` | No | True | Use TLS encryption |
| `EMAIL_HOST_USER` | No | - | SMTP username |
| `EMAIL_HOST_PASSWORD` | No | - | SMTP password |

### Performance Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENABLE_PERFORMANCE_MONITORING` | No | False | Enable performance monitoring |
| `SLOW_QUERY_THRESHOLD` | No | 1.0 | Slow query threshold (seconds) |
| `DB_CONN_MAX_AGE` | No | 600 | Database connection max age |

## Database Setup

### PostgreSQL Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### Database Configuration

1. **Create database and user:**
   ```sql
   sudo -u postgres psql
   CREATE DATABASE job_board_prod;
   CREATE USER job_board_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE job_board_prod TO job_board_user;
   ALTER USER job_board_user CREATEDB;
   \q
   ```

2. **Configure PostgreSQL:**
   ```bash
   # Edit postgresql.conf
   sudo nano /etc/postgresql/14/main/postgresql.conf
   
   # Optimize for production
   shared_buffers = 256MB
   effective_cache_size = 1GB
   maintenance_work_mem = 64MB
   checkpoint_completion_target = 0.9
   wal_buffers = 16MB
   default_statistics_target = 100
   random_page_cost = 1.1
   effective_io_concurrency = 200
   ```

3. **Configure authentication:**
   ```bash
   # Edit pg_hba.conf
   sudo nano /etc/postgresql/14/main/pg_hba.conf
   
   # Add line for application user
   local   job_board_prod   job_board_user   md5
   host    job_board_prod   job_board_user   127.0.0.1/32   md5
   ```

4. **Restart PostgreSQL:**
   ```bash
   sudo systemctl restart postgresql
   ```

### Database Performance Tuning

1. **Connection pooling:**
   ```python
   # In Django settings
   DATABASES = {
       'default': {
           'CONN_MAX_AGE': 600,
           'CONN_HEALTH_CHECKS': True,
           'OPTIONS': {
               'MAX_CONNS': 20,
               'MIN_CONNS': 5,
           }
       }
   }
   ```

2. **Indexes optimization:**
   ```bash
   # Run after migrations
   python manage.py dbshell --settings=config.settings.production
   ANALYZE;
   REINDEX DATABASE job_board_prod;
   ```

## SSL/TLS Configuration

### Let's Encrypt (Recommended)

1. **Install Certbot:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain certificate:**
   ```bash
   sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com
   ```

3. **Auto-renewal:**
   ```bash
   sudo crontab -e
   # Add line:
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

### Custom SSL Certificate

1. **Install certificate files:**
   ```bash
   sudo mkdir -p /etc/nginx/ssl
   sudo cp your-cert.pem /etc/nginx/ssl/cert.pem
   sudo cp your-key.pem /etc/nginx/ssl/key.pem
   sudo chmod 600 /etc/nginx/ssl/key.pem
   ```

2. **Configure nginx:**
   ```nginx
   server {
       listen 443 ssl http2;
       ssl_certificate /etc/nginx/ssl/cert.pem;
       ssl_certificate_key /etc/nginx/ssl/key.pem;
       # ... rest of configuration
   }
   ```

## Monitoring Setup

### Health Check Monitoring

1. **Set up monitoring service:**
   ```bash
   # Example with curl and cron
   crontab -e
   # Add line:
   */5 * * * * curl -f https://api.yourdomain.com/api/health/ || echo "Health check failed" | mail -s "API Down" admin@yourdomain.com
   ```

2. **Application metrics:**
   ```python
   # In Django settings
   INSTALLED_APPS += ['django_prometheus']
   MIDDLEWARE += ['django_prometheus.middleware.PrometheusBeforeMiddleware']
   MIDDLEWARE += ['django_prometheus.middleware.PrometheusAfterMiddleware']
   ```

### Log Monitoring

1. **Logrotate configuration:**
   ```bash
   sudo nano /etc/logrotate.d/django
   ```
   
   ```
   /var/log/django/*.log {
       daily
       missingok
       rotate 52
       compress
       delaycompress
       notifempty
       create 644 jobboard jobboard
       postrotate
           systemctl reload jobboard
       endscript
   }
   ```

2. **Log aggregation:**
   ```bash
   # Example with rsyslog
   sudo nano /etc/rsyslog.d/50-django.conf
   ```
   
   ```
   $ModLoad imfile
   $InputFileName /var/log/django/django.log
   $InputFileTag django:
   $InputFileStateFile stat-django
   $InputFileSeverity info
   $InputFileFacility local0
   $InputRunFileMonitor
   ```

### Performance Monitoring

1. **Database monitoring:**
   ```sql
   -- Enable pg_stat_statements
   CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
   
   -- Monitor slow queries
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;
   ```

2. **Application monitoring:**
   ```python
   # Custom middleware for performance tracking
   import time
   from django.db import connection
   
   class PerformanceMiddleware:
       def __init__(self, get_response):
           self.get_response = get_response
   
       def __call__(self, request):
           start_time = time.time()
           start_queries = len(connection.queries)
           
           response = self.get_response(request)
           
           end_time = time.time()
           end_queries = len(connection.queries)
           
           # Log performance metrics
           duration = end_time - start_time
           query_count = end_queries - start_queries
           
           if duration > 1.0:  # Log slow requests
               logger.warning(f"Slow request: {request.path} took {duration:.2f}s with {query_count} queries")
           
           return response
   ```

This environment setup guide provides comprehensive instructions for deploying the Job Board Backend API across different environments with proper security, performance, and monitoring configurations.