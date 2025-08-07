# Production Deployment Guide

This guide covers deploying the Job Board Backend API to production.

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)
- Environment variables configured

## Environment Variables

Copy `.env.example` to `.env` and configure the following required variables:

### Required Variables
```bash
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DB_NAME=your_production_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
```

### Optional Production Variables
```bash
# Database Connection Pooling
DB_CONN_MAX_AGE=600
DB_MAX_CONNECTIONS=20
DB_MIN_CONNECTIONS=5

# Logging
LOG_DIR=/var/log/django
LOG_LEVEL=INFO
ENABLE_STRUCTURED_LOGGING=True

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Health Checks
HEALTH_CHECK_ENABLED=True
HEALTH_CHECK_DATABASE=True
HEALTH_CHECK_CACHE=True
HEALTH_CHECK_STORAGE=True
```

## Deployment Steps

### 1. Automated Deployment

Use the provided deployment script:

```bash
# Make script executable
chmod +x scripts/deploy.py

# Run deployment
python scripts/deploy.py
```

### 2. Manual Deployment

```bash
# 1. Install dependencies
pip install -r requirements/base.txt

# 2. Run database migrations
python manage.py migrate --settings=config.settings.production

# 3. Collect static files
python manage.py collectstatic --noinput --settings=config.settings.production

# 4. Create superuser (optional)
python manage.py createsuperuser --settings=config.settings.production

# 5. Check production readiness
python manage.py check_production --settings=config.settings.production
```

## Health Check Endpoints

The application provides several health check endpoints for monitoring:

- `/api/health/` - Comprehensive health check
- `/api/health/live/` - Liveness probe (Kubernetes)
- `/api/health/ready/` - Readiness probe (Kubernetes)
- `/api/metrics/` - Basic system metrics

### Example Health Check Response

```json
{
    "status": "healthy",
    "timestamp": 1754534097.677,
    "total_response_time": 0.123,
    "checks": {
        "database": {
            "status": "healthy",
            "message": "Database is healthy",
            "response_time": 0.045
        },
        "cache": {
            "status": "healthy",
            "message": "Cache is healthy",
            "response_time": 0.012
        },
        "storage": {
            "status": "healthy",
            "message": "Storage is healthy",
            "response_time": 0.003
        }
    },
    "version": "1.0.0",
    "environment": "production"
}
```

## Production Checklist

Run the production readiness check:

```bash
python manage.py check_production --settings=config.settings.production
```

This will verify:
- [ ] DEBUG is disabled
- [ ] SECRET_KEY is properly configured
- [ ] ALLOWED_HOSTS is set
- [ ] Database connectivity
- [ ] Cache connectivity
- [ ] Static files configuration
- [ ] Media files configuration
- [ ] Log directories
- [ ] Security settings
- [ ] Required environment variables

## Logging

Production logging is configured with:

- **Structured JSON logging** (configurable)
- **Log rotation** with size limits
- **Multiple log files**:
  - `django.log` - General application logs
  - `audit.log` - Audit trail logs
  - `security.log` - Security-related logs
  - `performance.log` - Performance metrics
  - `errors.log` - Error logs only

### Log Configuration

```bash
# Log directory (must be writable)
LOG_DIR=/var/log/django

# Log levels
LOG_LEVEL=INFO
DB_LOG_LEVEL=WARNING

# Log rotation
LOG_MAX_BYTES=52428800  # 50MB
LOG_BACKUP_COUNT=10
```

## Database Configuration

### Connection Pooling

Production settings include optimized database connection pooling:

```python
DATABASES = {
    'default': {
        'CONN_MAX_AGE': 600,  # 10 minutes
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
            'connect_timeout': 10,
        }
    }
}
```

### Performance Optimization

- Connection pooling enabled
- Query optimization with indexes
- Prepared statement caching
- Health checks for connections

## Security Features

Production deployment includes:

- **HTTPS enforcement**
- **Secure cookies**
- **CSRF protection**
- **Security headers**
- **Rate limiting**
- **Audit logging**
- **Input validation**

## Monitoring

### Health Checks

Configure your monitoring system to check:

- `GET /api/health/live/` - Should return 200
- `GET /api/health/ready/` - Should return 200
- `GET /api/health/` - Detailed health status

### Metrics

Basic system metrics available at `/api/metrics/`:

- CPU usage
- Memory usage
- Disk usage
- Application memory
- Database connections

## Troubleshooting

### Common Issues

1. **Environment Variables Missing**
   ```bash
   python manage.py check_production
   ```

2. **Database Connection Issues**
   ```bash
   python manage.py check --database default --settings=config.settings.production
   ```

3. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --settings=config.settings.production
   ```

4. **Log Permission Issues**
   ```bash
   sudo mkdir -p /var/log/django
   sudo chown -R www-data:www-data /var/log/django
   ```

### Debug Mode

Never run production with `DEBUG=True`. If you need to debug production issues:

1. Check application logs
2. Use health check endpoints
3. Monitor system metrics
4. Review audit logs

## Performance Tuning

### Database

- Use connection pooling
- Optimize queries with indexes
- Monitor slow queries
- Use read replicas if needed

### Caching

- Configure Redis for production caching
- Use cache for session storage
- Cache frequently accessed data

### Static Files

- Use CDN for static files
- Enable compression
- Set proper cache headers

## Backup Strategy

1. **Database Backups**
   - Daily automated backups
   - Point-in-time recovery
   - Test restore procedures

2. **Media Files**
   - Regular file system backups
   - Cloud storage integration

3. **Configuration**
   - Version control for settings
   - Environment variable backups

## Scaling Considerations

- Use load balancers
- Horizontal scaling with multiple instances
- Database read replicas
- Redis clustering
- CDN for static content