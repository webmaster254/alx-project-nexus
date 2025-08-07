#!/usr/bin/env python
"""
Database migration script for job board backend.
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


class MigrationError(Exception):
    """Custom exception for migration errors."""
    pass


class DatabaseMigrator:
    """Database migration utility."""
    
    def __init__(self, settings_module='config.settings.production'):
        self.project_root = PROJECT_ROOT
        self.manage_py = self.project_root / 'manage.py'
        self.settings_module = settings_module
        
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
            raise MigrationError(error_msg)
    
    def check_database_connection(self):
        """Check if database is accessible."""
        logger.info("Checking database connection...")
        
        try:
            self.run_command(
                f"python {self.manage_py} check --database default --settings={self.settings_module}"
            )
            logger.info("Database connection successful")
        except MigrationError:
            logger.error("Database connection failed")
            raise
    
    def show_migration_status(self):
        """Show current migration status."""
        logger.info("Checking migration status...")
        
        try:
            output = self.run_command(
                f"python {self.manage_py} showmigrations --settings={self.settings_module}",
                capture_output=True
            )
            logger.info("Current migration status:")
            for line in output.split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
            return output
        except MigrationError as e:
            logger.warning(f"Could not check migration status: {e}")
            return ""
    
    def create_migrations(self, app_name=None):
        """Create new migrations for changes."""
        logger.info("Creating new migrations...")
        
        command = f"python {self.manage_py} makemigrations --settings={self.settings_module}"
        if app_name:
            command += f" {app_name}"
        
        try:
            output = self.run_command(command, capture_output=True)
            if "No changes detected" in output:
                logger.info("No new migrations needed")
            else:
                logger.info("New migrations created:")
                logger.info(output)
        except MigrationError as e:
            logger.error(f"Failed to create migrations: {e}")
            raise
    
    def run_migrations(self, app_name=None, fake=False, fake_initial=False):
        """Run database migrations."""
        logger.info("Running database migrations...")
        
        command = f"python {self.manage_py} migrate --settings={self.settings_module}"
        
        if app_name:
            command += f" {app_name}"
        if fake:
            command += " --fake"
        if fake_initial:
            command += " --fake-initial"
        
        try:
            output = self.run_command(command, capture_output=True)
            logger.info("Migration output:")
            for line in output.split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
            logger.info("Database migrations completed successfully")
        except MigrationError as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    def rollback_migration(self, app_name, migration_name):
        """Rollback to a specific migration."""
        logger.info(f"Rolling back {app_name} to {migration_name}...")
        
        command = f"python {self.manage_py} migrate {app_name} {migration_name} --settings={self.settings_module}"
        
        try:
            self.run_command(command)
            logger.info(f"Rollback to {app_name}.{migration_name} completed")
        except MigrationError as e:
            logger.error(f"Rollback failed: {e}")
            raise
    
    def backup_database(self, backup_file=None):
        """Create database backup before migrations."""
        if not backup_file:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"backup_{timestamp}.sql"
        
        logger.info(f"Creating database backup: {backup_file}")
        
        # Get database settings
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        
        if not db_name or not db_user:
            logger.warning("Database credentials not found, skipping backup")
            return
        
        backup_path = self.project_root / 'backups' / backup_file
        backup_path.parent.mkdir(exist_ok=True)
        
        command = f"pg_dump -h {db_host} -p {db_port} -U {db_user} -d {db_name} -f {backup_path}"
        
        try:
            self.run_command(command)
            logger.info(f"Database backup created: {backup_path}")
        except MigrationError as e:
            logger.warning(f"Backup failed: {e}")
    
    def validate_migrations(self):
        """Validate migration files for consistency."""
        logger.info("Validating migrations...")
        
        try:
            # Check for migration conflicts
            self.run_command(
                f"python {self.manage_py} makemigrations --check --dry-run --settings={self.settings_module}"
            )
            logger.info("Migration validation passed")
        except MigrationError as e:
            logger.error(f"Migration validation failed: {e}")
            raise


def main():
    """Main migration function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database migration utility')
    parser.add_argument('--settings', default='config.settings.production',
                       help='Django settings module')
    parser.add_argument('--backup', action='store_true',
                       help='Create database backup before migration')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check migration status')
    parser.add_argument('--create', action='store_true',
                       help='Create new migrations')
    parser.add_argument('--app', help='Specific app to migrate')
    parser.add_argument('--fake', action='store_true',
                       help='Mark migrations as run without executing')
    parser.add_argument('--fake-initial', action='store_true',
                       help='Mark initial migrations as run')
    parser.add_argument('--rollback', help='Rollback to specific migration (format: app.migration)')
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator(args.settings)
    
    try:
        # Check database connection
        migrator.check_database_connection()
        
        # Show current status
        migrator.show_migration_status()
        
        if args.check_only:
            logger.info("Check complete")
            return
        
        if args.create:
            migrator.create_migrations(args.app)
            return
        
        if args.rollback:
            if '.' not in args.rollback:
                logger.error("Rollback format should be: app.migration")
                sys.exit(1)
            app_name, migration_name = args.rollback.split('.', 1)
            migrator.rollback_migration(app_name, migration_name)
            return
        
        # Create backup if requested
        if args.backup:
            migrator.backup_database()
        
        # Validate migrations
        migrator.validate_migrations()
        
        # Run migrations
        migrator.run_migrations(
            app_name=args.app,
            fake=args.fake,
            fake_initial=args.fake_initial
        )
        
        # Show final status
        migrator.show_migration_status()
        
        logger.info("Migration process completed successfully")
        
    except MigrationError as e:
        logger.error(f"Migration process failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()