# Deployment Scripts

This directory contains scripts for deploying, managing, and maintaining the Job Board Backend API.

## Scripts Overview

### 1. `deploy.py` - Production Deployment
Automated deployment script that handles the complete deployment process.

**Usage:**
```bash
# Full deployment
python scripts/deploy.py

# Skip specific steps
python scripts/deploy.py --skip-migrations --skip-static --skip-superuser
```

**Features:**
- Environment validation
- Dependency installation
- Database migrations
- Static file collection
- Superuser creation
- Health checks

### 2. `migrate.py` - Database Migration Management
Comprehensive database migration utility with backup and rollback capabilities.

**Usage:**
```bash
# Check migration status
python scripts/migrate.py --check-only

# Create new migrations
python scripts/migrate.py --create --app jobs

# Run migrations with backup
python scripts/migrate.py --backup

# Rollback to specific migration
python scripts/migrate.py --rollback jobs.0003_add_performance_indexes

# Fake migrations (mark as applied without running)
python scripts/migrate.py --fake --app authentication
```

**Features:**
- Migration status checking
- Automatic backups before migration
- Rollback capabilities
- Migration validation
- Fake migration support

### 3. `backup.py` - Database Backup and Restore
Database backup and restore utility with compression and verification.

**Usage:**
```bash
# Create backup
python scripts/backup.py backup

# Create named backup
python scripts/backup.py backup --name pre_migration_backup

# Create uncompressed backup
python scripts/backup.py backup --no-compress

# List available backups
python scripts/backup.py list

# Restore from backup
python scripts/backup.py restore backup_20240101_120000.sql.gz

# Restore with database recreation
python scripts/backup.py restore backup_20240101_120000.sql.gz --drop

# Verify backup integrity
python scripts/backup.py verify backup_20240101_120000.sql.gz

# Clean up old backups (keep 10 most recent)
python scripts/backup.py cleanup --keep 10
```

**Features:**
- Compressed backups (gzip)
- Backup verification
- Automatic cleanup
- Database recreation
- Support for DATABASE_URL and individual DB parameters

### 4. `test_deployment.py` - Deployment Testing
Comprehensive deployment testing and validation script.

**Usage:**
```bash
# Test local deployment
python scripts/test_deployment.py

# Test remote deployment
python scripts/test_deployment.py --url https://api.yourdomain.com

# Test with custom timeout
python scripts/test_deployment.py --timeout 60 --wait-time 120
```

**Tests:**
- Service availability
- Health check endpoints
- API functionality
- Authentication endpoints
- Database connectivity
- Static file serving
- Security headers
- Performance metrics

### 5. `validate_deployment.py` - Deployment Validation
Pre-deployment validation to ensure configuration is correct.

**Usage:**
```bash
# Validate production configuration
python scripts/validate_deployment.py

# Validate with custom settings
python scripts/validate_deployment.py --settings config.settings.staging

# Output results to JSON
python scripts/validate_deployment.py --json-output validation_results.json
```

**Validations:**
- Environment variables
- Django configuration
- Database connectivity
- Static files setup
- Logging configuration
- Security settings
- Dependencies
- Docker configuration
- Backup setup

### 6. `init-db.sql` - Database Initialization
SQL script for initial database setup and optimization.

**Features:**
- PostgreSQL extensions setup
- Performance optimization settings
- Connection pooling configuration
- Index creation preparation

## Environment Variables

All scripts respect the following environment variables:

### Required
- `SECRET_KEY` - Django secret key
- `DB_NAME` / `DATABASE_URL` - Database configuration
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `ALLOWED_HOSTS` - Allowed hosts for Django

### Optional
- `LOG_DIR` - Log directory (default: `/var/log/django`)
- `STATIC_ROOT` - Static files directory (default: `/var/www/static`)
- `MEDIA_ROOT` - Media files directory (default: `/var/www/media`)
- `ADMIN_EMAIL` - Admin user email for superuser creation
- `ADMIN_PASSWORD` - Admin user password for superuser creation

## Common Workflows

### Initial Deployment
```bash
# 1. Validate configuration
python scripts/validate_deployment.py

# 2. Create database backup (if upgrading)
python scripts/backup.py backup --name pre_deployment

# 3. Run deployment
python scripts/deploy.py

# 4. Test deployment
python scripts/test_deployment.py
```

### Database Migration
```bash
# 1. Create backup
python scripts/backup.py backup --name pre_migration

# 2. Check migration status
python scripts/migrate.py --check-only

# 3. Run migrations
python scripts/migrate.py

# 4. Verify deployment
python scripts/test_deployment.py
```

### Rollback Procedure
```bash
# 1. Stop application
sudo systemctl stop jobboard

# 2. Restore database
python scripts/backup.py restore backup_20240101_120000.sql.gz --drop

# 3. Rollback migrations if needed
python scripts/migrate.py --rollback jobs.0002_previous_migration

# 4. Start application
sudo systemctl start jobboard

# 5. Test
python scripts/test_deployment.py
```

### Regular Maintenance
```bash
# Weekly backup cleanup
python scripts/backup.py cleanup --keep 20

# Monthly validation
python scripts/validate_deployment.py

# Performance testing
python scripts/test_deployment.py --url https://api.yourdomain.com
```

## Error Handling

All scripts include comprehensive error handling:

- **Validation errors** - Configuration issues
- **Connection errors** - Database/network issues
- **Permission errors** - File system access issues
- **Command failures** - External command execution issues

## Logging

Scripts use Python's logging module with:

- **INFO level** - Normal operations
- **WARNING level** - Non-critical issues
- **ERROR level** - Critical failures
- **DEBUG level** - Detailed debugging (use `-v` flag)

## Security Considerations

- Scripts validate security settings
- Database credentials are handled securely
- Backup files are created with appropriate permissions
- Production checks prevent dangerous operations

## Integration with CI/CD

These scripts are designed to integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Validate Deployment
  run: python scripts/validate_deployment.py

- name: Deploy Application
  run: python scripts/deploy.py

- name: Test Deployment
  run: python scripts/test_deployment.py --url ${{ secrets.PRODUCTION_URL }}
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x scripts/*.py
   sudo chown -R $USER:$USER /var/log/django
   ```

2. **Database Connection Failed**
   ```bash
   # Check environment variables
   echo $DATABASE_URL
   # Test connection
   python scripts/migrate.py --check-only
   ```

3. **Static Files Not Found**
   ```bash
   python scripts/deploy.py --skip-migrations --skip-superuser
   ```

4. **Migration Conflicts**
   ```bash
   python scripts/migrate.py --create
   python scripts/migrate.py --fake-initial
   ```

### Getting Help

Each script includes help documentation:
```bash
python scripts/deploy.py --help
python scripts/migrate.py --help
python scripts/backup.py --help
python scripts/test_deployment.py --help
python scripts/validate_deployment.py --help
```

## Best Practices

1. **Always validate** before deployment
2. **Create backups** before major changes
3. **Test deployments** in staging first
4. **Monitor logs** during deployment
5. **Keep scripts updated** with application changes
6. **Document custom procedures** for your environment
7. **Regular maintenance** and cleanup
8. **Security reviews** of deployment procedures