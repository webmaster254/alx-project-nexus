#!/usr/bin/env python
"""
Comprehensive deployment validation script.
Validates all aspects of the deployment before going live.
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DeploymentValidator:
    """Comprehensive deployment validation utility."""
    
    def __init__(self, settings_module='config.settings.production'):
        self.project_root = PROJECT_ROOT
        self.manage_py = self.project_root / 'manage.py'
        self.settings_module = settings_module
        self.validation_results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def run_command(self, command, check=True, capture_output=False):
        """Run a shell command with error handling."""
        logger.debug(f"Running: {command}")
        
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=check,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                return result.stdout.strip()
            else:
                subprocess.run(
                    command,
                    shell=True,
                    check=check,
                    cwd=self.project_root
                )
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {command}"
            if capture_output and e.stderr:
                error_msg += f"\nError: {e.stderr}"
            raise ValidationError(error_msg)
    
    def add_result(self, category, test_name, message):
        """Add validation result."""
        self.validation_results[category].append({
            'test': test_name,
            'message': message
        })
        
        if category == 'passed':
            logger.info(f"✓ {test_name}: {message}")
        elif category == 'failed':
            logger.error(f"✗ {test_name}: {message}")
        else:  # warnings
            logger.warning(f"⚠ {test_name}: {message}")
    
    def validate_environment_variables(self):
        """Validate required environment variables."""
        logger.info("Validating environment variables...")
        
        required_vars = {
            'SECRET_KEY': 'Django secret key',
            'DB_NAME': 'Database name',
            'DB_USER': 'Database user',
            'DB_PASSWORD': 'Database password',
            'DB_HOST': 'Database host',
            'ALLOWED_HOSTS': 'Allowed hosts',
        }
        
        # Check if DATABASE_URL is provided as alternative
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # Remove individual DB vars from required if DATABASE_URL exists
            for key in ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']:
                required_vars.pop(key, None)
            self.add_result('passed', 'Database Configuration', 'DATABASE_URL provided')
        
        missing_vars = []
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing_vars.append(f"{var} ({description})")
            elif var == 'SECRET_KEY' and len(value) < 50:
                self.add_result('warnings', 'SECRET_KEY', 'Secret key is shorter than recommended (50+ chars)')
            elif var == 'DEBUG' and value.lower() == 'true':
                self.add_result('failed', 'DEBUG Setting', 'DEBUG is enabled in production')
            else:
                self.add_result('passed', f'{var}', f'{description} is configured')
        
        if missing_vars:
            self.add_result('failed', 'Environment Variables', f'Missing: {", ".join(missing_vars)}')
        else:
            self.add_result('passed', 'Environment Variables', 'All required variables are set')
    
    def validate_django_configuration(self):
        """Validate Django configuration."""
        logger.info("Validating Django configuration...")
        
        try:
            # Run Django system check
            output = self.run_command(
                f"python {self.manage_py} check --settings={self.settings_module}",
                capture_output=True
            )
            
            if "System check identified no issues" in output:
                self.add_result('passed', 'Django System Check', 'No issues found')
            else:
                self.add_result('warnings', 'Django System Check', 'Some issues found')
                logger.info(f"Django check output: {output}")
                
        except ValidationError as e:
            self.add_result('failed', 'Django System Check', f'Failed: {e}')
    
    def validate_database_connectivity(self):
        """Validate database connectivity."""
        logger.info("Validating database connectivity...")
        
        try:
            # Test database connection
            self.run_command(
                f"python {self.manage_py} check --database default --settings={self.settings_module}"
            )
            self.add_result('passed', 'Database Connectivity', 'Database connection successful')
            
            # Check migration status
            output = self.run_command(
                f"python {self.manage_py} showmigrations --settings={self.settings_module}",
                capture_output=True
            )
            
            if '[X]' in output and '[ ]' not in output:
                self.add_result('passed', 'Database Migrations', 'All migrations applied')
            elif '[ ]' in output:
                self.add_result('warnings', 'Database Migrations', 'Some migrations not applied')
            else:
                self.add_result('warnings', 'Database Migrations', 'Could not determine migration status')
                
        except ValidationError as e:
            self.add_result('failed', 'Database Connectivity', f'Failed: {e}')
    
    def validate_static_files(self):
        """Validate static files configuration."""
        logger.info("Validating static files...")
        
        try:
            # Check if static files are collected
            static_root = os.getenv('STATIC_ROOT', '/var/www/static')
            static_path = Path(static_root)
            
            if static_path.exists() and any(static_path.iterdir()):
                self.add_result('passed', 'Static Files', f'Static files found in {static_root}')
            else:
                # Try to collect static files
                try:
                    self.run_command(
                        f"python {self.manage_py} collectstatic --noinput --settings={self.settings_module}"
                    )
                    self.add_result('passed', 'Static Files', 'Static files collected successfully')
                except ValidationError:
                    self.add_result('failed', 'Static Files', 'Could not collect static files')
                    
        except Exception as e:
            self.add_result('warnings', 'Static Files', f'Could not validate: {e}')
    
    def validate_logging_configuration(self):
        """Validate logging configuration."""
        logger.info("Validating logging configuration...")
        
        log_dir = os.getenv('LOG_DIR', '/var/log/django')
        log_path = Path(log_dir)
        
        try:
            # Check if log directory exists and is writable
            if log_path.exists():
                # Test write permissions
                test_file = log_path / 'test_write.tmp'
                try:
                    test_file.write_text('test')
                    test_file.unlink()
                    self.add_result('passed', 'Log Directory', f'Log directory {log_dir} is writable')
                except PermissionError:
                    self.add_result('failed', 'Log Directory', f'Log directory {log_dir} is not writable')
            else:
                self.add_result('warnings', 'Log Directory', f'Log directory {log_dir} does not exist')
                
        except Exception as e:
            self.add_result('warnings', 'Logging Configuration', f'Could not validate: {e}')
    
    def validate_security_settings(self):
        """Validate security settings."""
        logger.info("Validating security settings...")
        
        security_checks = {
            'DEBUG': ('False', 'DEBUG should be False in production'),
            'SECURE_SSL_REDIRECT': ('True', 'SSL redirect should be enabled'),
            'SESSION_COOKIE_SECURE': ('True', 'Session cookies should be secure'),
            'CSRF_COOKIE_SECURE': ('True', 'CSRF cookies should be secure'),
        }
        
        for setting, (expected, description) in security_checks.items():
            value = os.getenv(setting, '').lower()
            if value == expected.lower():
                self.add_result('passed', f'Security - {setting}', description)
            else:
                self.add_result('warnings', f'Security - {setting}', f'{description} (current: {value})')
    
    def validate_dependencies(self):
        """Validate Python dependencies."""
        logger.info("Validating dependencies...")
        
        try:
            # Check if requirements are installed
            requirements_file = self.project_root / 'requirements' / 'base.txt'
            if requirements_file.exists():
                # This is a basic check - in production you might want more sophisticated validation
                self.add_result('passed', 'Dependencies', 'Requirements file found')
            else:
                self.add_result('warnings', 'Dependencies', 'Requirements file not found')
                
        except Exception as e:
            self.add_result('warnings', 'Dependencies', f'Could not validate: {e}')
    
    def validate_docker_configuration(self):
        """Validate Docker configuration if applicable."""
        logger.info("Validating Docker configuration...")
        
        dockerfile = self.project_root / 'Dockerfile'
        docker_compose = self.project_root / 'docker-compose.yml'
        docker_compose_prod = self.project_root / 'docker-compose.prod.yml'
        
        if dockerfile.exists():
            self.add_result('passed', 'Docker - Dockerfile', 'Dockerfile found')
        else:
            self.add_result('warnings', 'Docker - Dockerfile', 'Dockerfile not found')
        
        if docker_compose.exists():
            self.add_result('passed', 'Docker - Development', 'docker-compose.yml found')
        else:
            self.add_result('warnings', 'Docker - Development', 'docker-compose.yml not found')
        
        if docker_compose_prod.exists():
            self.add_result('passed', 'Docker - Production', 'docker-compose.prod.yml found')
        else:
            self.add_result('warnings', 'Docker - Production', 'docker-compose.prod.yml not found')
    
    def validate_backup_configuration(self):
        """Validate backup configuration."""
        logger.info("Validating backup configuration...")
        
        backup_script = self.project_root / 'scripts' / 'backup.py'
        backup_dir = self.project_root / 'backups'
        
        if backup_script.exists():
            self.add_result('passed', 'Backup - Script', 'Backup script found')
        else:
            self.add_result('warnings', 'Backup - Script', 'Backup script not found')
        
        if backup_dir.exists():
            self.add_result('passed', 'Backup - Directory', 'Backup directory exists')
        else:
            self.add_result('warnings', 'Backup - Directory', 'Backup directory not found')
    
    def run_all_validations(self):
        """Run all validation checks."""
        logger.info("Starting comprehensive deployment validation...")
        
        validation_methods = [
            self.validate_environment_variables,
            self.validate_django_configuration,
            self.validate_database_connectivity,
            self.validate_static_files,
            self.validate_logging_configuration,
            self.validate_security_settings,
            self.validate_dependencies,
            self.validate_docker_configuration,
            self.validate_backup_configuration,
        ]
        
        for validation_method in validation_methods:
            try:
                validation_method()
            except Exception as e:
                self.add_result('failed', validation_method.__name__, f'Validation error: {e}')
        
        # Print summary
        self.print_summary()
        
        # Return success status
        return len(self.validation_results['failed']) == 0
    
    def print_summary(self):
        """Print validation summary."""
        logger.info("\n" + "="*60)
        logger.info("DEPLOYMENT VALIDATION SUMMARY")
        logger.info("="*60)
        
        passed_count = len(self.validation_results['passed'])
        failed_count = len(self.validation_results['failed'])
        warning_count = len(self.validation_results['warnings'])
        
        logger.info(f"✓ Passed: {passed_count}")
        logger.info(f"✗ Failed: {failed_count}")
        logger.info(f"⚠ Warnings: {warning_count}")
        
        if failed_count > 0:
            logger.info("\nFAILED CHECKS:")
            for result in self.validation_results['failed']:
                logger.info(f"  ✗ {result['test']}: {result['message']}")
        
        if warning_count > 0:
            logger.info("\nWARNINGS:")
            for result in self.validation_results['warnings']:
                logger.info(f"  ⚠ {result['test']}: {result['message']}")
        
        logger.info("\n" + "="*60)
        
        if failed_count == 0:
            logger.info("🎉 DEPLOYMENT VALIDATION PASSED!")
            logger.info("Your deployment is ready for production.")
        else:
            logger.error("❌ DEPLOYMENT VALIDATION FAILED!")
            logger.error("Please fix the failed checks before deploying to production.")
        
        logger.info("="*60)


def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate deployment configuration')
    parser.add_argument('--settings', default='config.settings.production',
                       help='Django settings module')
    parser.add_argument('--json-output', help='Output results to JSON file')
    
    args = parser.parse_args()
    
    validator = DeploymentValidator(args.settings)
    
    try:
        success = validator.run_all_validations()
        
        # Output JSON if requested
        if args.json_output:
            with open(args.json_output, 'w') as f:
                json.dump(validator.validation_results, f, indent=2)
            logger.info(f"Validation results saved to: {args.json_output}")
        
        if success:
            logger.info("Deployment validation completed successfully!")
            sys.exit(0)
        else:
            logger.error("Deployment validation failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Validation failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()