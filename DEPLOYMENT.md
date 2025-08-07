# Job Board Backend - Deployment Guide

This comprehensive guide covers all aspects of deploying the Job Board Backend API to various environments.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Database Management](#database-management)
6. [Monitoring and Health Checks](#monitoring-and-health-checks)
7. [Troubleshooting](#troubleshooting)
8. [Security Considerations](#security-considerations)

## Quick Start

### Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd job-board-backend

# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate --settings=config.settings.development

# Create superuser
docker-compose exec web python manage.py createsuperuser --settings=config.settings.development
```

### Production Environment

```bash
# Set up environment variables
cp .env.example .env
# Edit .env with production values

# Deploy with production Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Run deployment script
python scripts/deploy.py

# Test deployment
python scripts/test_deployment.py --url https://your-domain.com
```

## Environment Setup

### Required Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Core Django Settings
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database
# OR individual parameters:
DB_NAME=job_board_prod
DB_USER=job_board_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Logging
LOG_DIR=/var/log/django
LOG_LEVEL=INFO
```

### Optional Configuration

```bash
# Redis for caching
REDIS_URL=redis://localhost:6379/1

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Static/Media files
STATIC_ROOT=/var/www/static
MEDIA_ROOT=/var/www/media

# Performance monitoring
ENABLE_PERFORMANCE_MONITORING=True
SLOW_QUERY_THRESHOLD=1.0
```

## Docker Deployment

### Development with Docker

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f web

# Run management commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Stop services
docker-compose down
```

### Production with Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Check service health
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs web

# Scale web service
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

### Docker Configuration

The project includes optimized Docker configurations:

- **Multi-stage builds** for smaller production images
- **Health checks** for all services
- **Volume mounts** for persistent data
- **Environment-specific** configurations
- **Security hardening** with non-root users

## Production Deployment

### Manual Deployment

1. **Prepare the server:**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3.11 python3.11-venv postgresql-client nginx

   # Create application user
   sudo useradd -m -s /bin/bash jobboard
   sudo su - jobboard
   ```

2. **Set up the application:**
   ```bash
   # Clone repository
   git clone <repository-url> /home/jobboard/app
   cd /home/jobboard/app

   # Create virtual environment
   python3.11 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements/base.txt
   pip install gunicorn
   ```

3. **Configure environment:**
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   nano .env
   ```

4. **Run deployment script:**
   ```bash
   # Make script executable
   chmod +x scripts/deploy.py

   # Run deployment
   python scripts/deploy.py
   ```

### Automated Deployment Script

The `scripts/deploy.py` script handles:

- Environment validation
- Dependency installation
- Database migrations
- Static file collection
- Superuser creation
- Health checks

Usage:
```bash
# Full deployment
python scripts/deploy.py

# Skip specific steps
python scripts/deploy.py --skip-migrations --skip-static
```

### Systemd Service Configuration

Create `/etc/systemd/system/jobboard.service`:

```ini
[Unit]
Description=Job Board Backend
After=network.target postgresql.service

[Service]
Type=exec
User=jobboard
Group=jobboard
WorkingDirectory=/home/jobboard/app
Environment=PATH=/home/jobboard/app/venv/bin
EnvironmentFile=/home/jobboard/app/.env
ExecStart=/home/jobboard/app/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable jobboard
sudo systemctl start jobboard
sudo systemctl status jobboard
```

## Database Management

### Migration Scripts

Use the migration utility for database operations:

```bash
# Check migration status
python scripts/migrate.py --check-only

# Create new migrations
python scripts/migrate.py --create

# Run migrations with backup
python scripts/migrate.py --backup

# Rollback to specific migration
python scripts/migrate.py --rollback jobs.0003_add_performance_indexes
```

### Database Backup and Restore

```bash
# Create backup
pg_dump -h localhost -U job_board_user -d job_board_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -h localhost -U job_board_user -d job_board_prod < backup_20240101_120000.sql
```

### Performance Optimization

The database includes optimized configurations:

- **Connection pooling** with configurable limits
- **Performance indexes** on frequently queried fields
- **Full-text search** with PostgreSQL GIN indexes
- **Query optimization** with prepared statements

## Monitoring and Health Checks

### Health Check Endpoints

- `/api/health/live/` - Liveness probe (basic service check)
- `/api/health/ready/` - Readiness probe (dependencies check)
- `/api/health/` - Comprehensive health status

### Testing Deployment

Use the deployment testing script:

```bash
# Test local deployment
python scripts/test_deployment.py

# Test remote deployment
python scripts/test_deployment.py --url https://api.yourdomain.com

# Test with custom timeout
python scripts/test_deployment.py --timeout 60
```

The test script validates:
- Service availability
- Health check endpoints
- API functionality
- Database connectivity
- Static file serving
- Security headers
- Performance metrics

### Production Readiness Check

```bash
# Run production readiness check
python manage.py check_production --settings=config.settings.production
```

This validates:
- Environment variables
- Security settings
- Database connectivity
- Log directory permissions
- Static file configuration

### Monitoring Integration

Configure monitoring tools to check:

1. **Health endpoints** (every 30 seconds)
2. **Response times** (< 1 second for health checks)
3. **Error rates** (< 1% error rate)
4. **Database connections** (monitor pool usage)
5. **Log files** (watch for errors and warnings)

## Troubleshooting

### Common Issues

1. **Service won't start:**
   ```bash
   # Check logs
   docker-compose logs web
   # or
   sudo journalctl -u jobboard -f

   # Check environment variables
   python scripts/deploy.py --check-only
   ```

2. **Database connection errors:**
   ```bash
   # Test database connectivity
   python manage.py check --database default --settings=config.settings.production

   # Check database status
   sudo systemctl status postgresql
   ```

3. **Static files not loading:**
   ```bash
   # Collect static files
   python manage.py collectstatic --settings=config.settings.production

   # Check nginx configuration
   sudo nginx -t
   sudo systemctl reload nginx
   ```

4. **Permission errors:**
   ```bash
   # Fix log directory permissions
   sudo mkdir -p /var/log/django
   sudo chown -R jobboard:jobboard /var/log/django

   # Fix static file permissions
   sudo chown -R jobboard:jobboard /var/www/static
   ```

### Debug Mode

Never run production with `DEBUG=True`. For debugging:

1. Check application logs in `/var/log/django/`
2. Use health check endpoints for status
3. Monitor system metrics
4. Review audit logs for security events

### Log Files

Production logging includes:

- `django.log` - General application logs
- `audit.log` - Audit trail logs
- `security.log` - Security-related logs
- `performance.log` - Performance metrics
- `errors.log` - Error logs only

## Security Considerations

### Production Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` configured
- [ ] `ALLOWED_HOSTS` properly set
- [ ] HTTPS enforced (`SECURE_SSL_REDIRECT=True`)
- [ ] Secure cookies enabled
- [ ] Database credentials secured
- [ ] Log files protected (proper permissions)
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] Regular security updates applied

### SSL/TLS Configuration

For HTTPS deployment:

1. **Obtain SSL certificates** (Let's Encrypt recommended)
2. **Configure nginx** with SSL settings
3. **Enable security headers** in Django settings
4. **Test SSL configuration** with SSL Labs

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP (redirect to HTTPS)
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Regular Maintenance

1. **Update dependencies** regularly
2. **Monitor security advisories**
3. **Rotate secrets** periodically
4. **Review access logs** for suspicious activity
5. **Backup data** regularly
6. **Test disaster recovery** procedures

## Performance Tuning

### Application Performance

- Use **connection pooling** for database
- Enable **caching** with Redis
- Optimize **database queries** with indexes
- Use **CDN** for static files
- Configure **load balancing** for multiple instances

### Database Performance

- Monitor **slow queries** (threshold: 1 second)
- Use **read replicas** for scaling
- Optimize **connection pooling** settings
- Regular **VACUUM** and **ANALYZE** operations

### Infrastructure Scaling

- **Horizontal scaling** with load balancers
- **Database read replicas** for read-heavy workloads
- **Redis clustering** for cache scaling
- **CDN integration** for global content delivery

This deployment guide provides comprehensive coverage of all deployment scenarios and operational considerations for the Job Board Backend API.