#!/usr/bin/env python
"""
Production deployment script for job board backend.
"""

import os
import sys
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


class DeploymentError(Exception):
    """Custom exception for deployment errors."""
    pass


class ProductionDeployer:
    """Production deployment utility."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.manage_py = self.project_root / 'manage.py'
        
    def run_command(self, command, check=True, capture_output=False):
        """Run a shell command with error handling."""
        logger.info(f"Running: {command}")
        
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
            logger.error(error_msg)
            raise DeploymentError(error_msg)
    
    def check_environment(self):
        """Check if all required environment variables are set."""
        logger.info("Checking environment variables...")
        
        required_vars = [
            'SECRET_KEY',
            'DB_NAME',
            'DB_USER',
            'DB_PASSWORD',
            'DB_HOST',
            'ALLOWED_HOSTS',
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise DeploymentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        logger.info("Environment variables check passed")
    
    def install_dependencies(self):
        """Install Python dependencies."""
        logger.info("Installing dependencies...")
        
        requirements_file = self.project_root / 'requirements' / 'base.txt'
        if not requirements_file.exists():
            raise DeploymentError(f"Requirements file not found: {requirements_file}")
        
        self.run_command(f"pip install -r {requirements_file}")
        logger.info("Dependencies installed successfully")
    
    def collect_static_files(self):
        """Collect static files for production."""
        logger.info("Collecting static files...")
        
        self.run_command(
            f"python {self.manage_py} collectstatic --noinput --settings=config.settings.production"
        )
        logger.info("Static files collected successfully")
    
    def run_migrations(self):
        """Run database migrations."""
        logger.info("Running database migrations...")
        
        # Check migration status first
        try:
            output = self.run_command(
                f"python {self.manage_py} showmigrations --settings=config.settings.production",
                capture_output=True
            )
            logger.info("Current migration status:")
            logger.info(output)
        except DeploymentError:
            logger.warning("Could not check migration status")
        
        # Run migrations
        self.run_command(
            f"python {self.manage_py} migrate --settings=config.settings.production"
        )
        logger.info("Database migrations completed successfully")
    
    def create_superuser(self):
        """Create superuser if it doesn't exist."""
        logger.info("Checking for superuser...")
        
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if not admin_email or not admin_password:
            logger.warning("ADMIN_EMAIL or ADMIN_PASSWORD not set, skipping superuser creation")
            return
        
        try:
            # Check if superuser exists
            check_command = f"""
            python {self.manage_py} shell --settings=config.settings.production -c "
from apps.authentication.models import User
if User.objects.filter(email='{admin_email}', is_superuser=True).exists():
    print('EXISTS')
else:
    print('NOT_EXISTS')
"
            """
            
            result = self.run_command(check_command, capture_output=True)
            
            if 'NOT_EXISTS' in result:
                logger.info("Creating superuser...")
                create_command = f"""
                python {self.manage_py} shell --settings=config.settings.production -c "
from apps.authentication.models import User
User.objects.create_superuser(
    email='{admin_email}',
    password='{admin_password}',
    is_admin=True
)
print('Superuser created successfully')
"
                """
                self.run_command(create_command)
                logger.info("Superuser created successfully")
            else:
                logger.info("Superuser already exists")
                
        except DeploymentError as e:
            logger.warning(f"Could not create superuser: {e}")
    
    def run_health_check(self):
        """Run health check to verify deployment."""
        logger.info("Running health check...")
        
        try:
            # Test database connection
            self.run_command(
                f"python {self.manage_py} check --database default --settings=config.settings.production"
            )
            
            # Test Django system check
            self.run_command(
                f"python {self.manage_py} check --settings=config.settings.production"
            )
            
            logger.info("Health check passed")
            
        except DeploymentError as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    def setup_log_directories(self):
        """Create log directories if they don't exist."""
        logger.info("Setting up log directories...")
        
        log_dir = os.getenv('LOG_DIR', '/var/log/django')
        log_path = Path(log_dir)
        
        try:
            log_path.mkdir(parents=True, exist_ok=True)
            
            # Set appropriate permissions
            os.chmod(log_path, 0o755)
            
            logger.info(f"Log directory created: {log_path}")
            
        except PermissionError:
            logger.warning(f"Could not create log directory {log_path} - check permissions")
        except Exception as e:
            logger.warning(f"Error setting up log directories: {e}")
    
    def deploy(self, skip_migrations=False, skip_static=False, skip_superuser=False):
        """Run full deployment process."""
        logger.info("Starting production deployment...")
        
        try:
            # Pre-deployment checks
            self.check_environment()
            self.setup_log_directories()
            
            # Install dependencies
            self.install_dependencies()
            
            # Database operations
            if not skip_migrations:
                self.run_migrations()
            
            # Static files
            if not skip_static:
                self.collect_static_files()
            
            # Create superuser
            if not skip_superuser:
                self.create_superuser()
            
            # Post-deployment verification
            self.run_health_check()
            
            logger.info("Deployment completed successfully!")
            
        except DeploymentError as e:
            logger.error(f"Deployment failed: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error during deployment: {e}")
            sys.exit(1)


def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy job board backend to production')
    parser.add_argument('--skip-migrations', action='store_true', help='Skip database migrations')
    parser.add_argument('--skip-static', action='store_true', help='Skip static file collection')
    parser.add_argument('--skip-superuser', action='store_true', help='Skip superuser creation')
    
    args = parser.parse_args()
    
    deployer = ProductionDeployer()
    deployer.deploy(
        skip_migrations=args.skip_migrations,
        skip_static=args.skip_static,
        skip_superuser=args.skip_superuser
    )


if __name__ == '__main__':
    main()