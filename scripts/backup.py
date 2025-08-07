#!/usr/bin/env python
"""
Database backup and restore script for job board backend.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
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


class BackupError(Exception):
    """Custom exception for backup errors."""
    pass


class DatabaseBackup:
    """Database backup and restore utility."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.backup_dir = self.project_root / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
        
        # Get database configuration from environment
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        
        # Check if DATABASE_URL is provided instead
        self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url and not all([self.db_name, self.db_user, self.db_password]):
            raise BackupError("Database configuration not found. Set DATABASE_URL or individual DB_* variables.")
    
    def run_command(self, command, check=True, capture_output=False, env=None):
        """Run a shell command with error handling."""
        logger.info(f"Running: {command}")
        
        # Set up environment with password if needed
        cmd_env = os.environ.copy()
        if env:
            cmd_env.update(env)
        if self.db_password and not self.database_url:
            cmd_env['PGPASSWORD'] = self.db_password
        
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=check,
                    capture_output=True,
                    text=True,
                    env=cmd_env,
                    cwd=self.project_root
                )
                return result.stdout.strip()
            else:
                subprocess.run(
                    command,
                    shell=True,
                    check=check,
                    env=cmd_env,
                    cwd=self.project_root
                )
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {command}"
            if capture_output and e.stderr:
                error_msg += f"\nError: {e.stderr}"
            logger.error(error_msg)
            raise BackupError(error_msg)
    
    def create_backup(self, backup_name=None, compress=True):
        """Create a database backup."""
        if not backup_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
        
        if compress:
            backup_file = self.backup_dir / f"{backup_name}.sql.gz"
            compress_cmd = " | gzip"
        else:
            backup_file = self.backup_dir / f"{backup_name}.sql"
            compress_cmd = ""
        
        logger.info(f"Creating database backup: {backup_file}")
        
        if self.database_url:
            # Use DATABASE_URL
            command = f"pg_dump '{self.database_url}'{compress_cmd} > {backup_file}"
        else:
            # Use individual parameters
            command = f"pg_dump -h {self.db_host} -p {self.db_port} -U {self.db_user} -d {self.db_name}{compress_cmd} > {backup_file}"
        
        try:
            self.run_command(command)
            
            # Verify backup file was created and has content
            if backup_file.exists() and backup_file.stat().st_size > 0:
                size_mb = backup_file.stat().st_size / (1024 * 1024)
                logger.info(f"Backup created successfully: {backup_file} ({size_mb:.2f} MB)")
                return str(backup_file)
            else:
                raise BackupError("Backup file was not created or is empty")
                
        except BackupError:
            # Clean up failed backup file
            if backup_file.exists():
                backup_file.unlink()
            raise
    
    def restore_backup(self, backup_file, drop_existing=False):
        """Restore database from backup."""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            # Try looking in backup directory
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                raise BackupError(f"Backup file not found: {backup_file}")
        
        logger.info(f"Restoring database from: {backup_path}")
        
        # Determine if file is compressed
        is_compressed = backup_path.suffix == '.gz'
        
        if drop_existing:
            logger.warning("Dropping existing database...")
            if self.database_url:
                # Extract database name from URL for dropping
                import urllib.parse
                parsed = urllib.parse.urlparse(self.database_url)
                db_name = parsed.path.lstrip('/')
                drop_cmd = f"dropdb '{parsed.scheme}://{parsed.netloc}/{db_name}'"
                create_cmd = f"createdb '{parsed.scheme}://{parsed.netloc}/{db_name}'"
            else:
                drop_cmd = f"dropdb -h {self.db_host} -p {self.db_port} -U {self.db_user} {self.db_name}"
                create_cmd = f"createdb -h {self.db_host} -p {self.db_port} -U {self.db_user} {self.db_name}"
            
            try:
                self.run_command(drop_cmd, check=False)  # Don't fail if DB doesn't exist
                self.run_command(create_cmd)
            except BackupError as e:
                logger.warning(f"Could not recreate database: {e}")
        
        # Restore command
        if is_compressed:
            decompress_cmd = "gunzip -c"
        else:
            decompress_cmd = "cat"
        
        if self.database_url:
            command = f"{decompress_cmd} {backup_path} | psql '{self.database_url}'"
        else:
            command = f"{decompress_cmd} {backup_path} | psql -h {self.db_host} -p {self.db_port} -U {self.db_user} -d {self.db_name}"
        
        try:
            self.run_command(command)
            logger.info("Database restored successfully")
        except BackupError:
            logger.error("Database restore failed")
            raise
    
    def list_backups(self):
        """List available backup files."""
        logger.info("Available backups:")
        
        backup_files = []
        for pattern in ['*.sql', '*.sql.gz']:
            backup_files.extend(self.backup_dir.glob(pattern))
        
        if not backup_files:
            logger.info("No backup files found")
            return []
        
        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for backup_file in backup_files:
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
            logger.info(f"  {backup_file.name} - {size_mb:.2f} MB - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return [str(f) for f in backup_files]
    
    def cleanup_old_backups(self, keep_count=10):
        """Remove old backup files, keeping only the most recent ones."""
        logger.info(f"Cleaning up old backups, keeping {keep_count} most recent...")
        
        backup_files = []
        for pattern in ['*.sql', '*.sql.gz']:
            backup_files.extend(self.backup_dir.glob(pattern))
        
        if len(backup_files) <= keep_count:
            logger.info(f"Only {len(backup_files)} backups found, no cleanup needed")
            return
        
        # Sort by modification time (oldest first for deletion)
        backup_files.sort(key=lambda x: x.stat().st_mtime)
        
        files_to_delete = backup_files[:-keep_count]
        
        for backup_file in files_to_delete:
            logger.info(f"Removing old backup: {backup_file.name}")
            backup_file.unlink()
        
        logger.info(f"Cleaned up {len(files_to_delete)} old backup files")
    
    def verify_backup(self, backup_file):
        """Verify backup file integrity."""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                raise BackupError(f"Backup file not found: {backup_file}")
        
        logger.info(f"Verifying backup: {backup_path}")
        
        # Check file size
        if backup_path.stat().st_size == 0:
            raise BackupError("Backup file is empty")
        
        # Check if compressed file is valid
        if backup_path.suffix == '.gz':
            try:
                self.run_command(f"gunzip -t {backup_path}")
                logger.info("Compressed backup file is valid")
            except BackupError:
                raise BackupError("Compressed backup file is corrupted")
        
        # Try to read SQL content
        try:
            if backup_path.suffix == '.gz':
                content = self.run_command(f"gunzip -c {backup_path} | head -10", capture_output=True)
            else:
                content = self.run_command(f"head -10 {backup_path}", capture_output=True)
            
            if 'PostgreSQL database dump' in content or 'CREATE' in content or 'INSERT' in content:
                logger.info("Backup file contains valid SQL content")
            else:
                logger.warning("Backup file may not contain valid SQL content")
                
        except BackupError:
            logger.warning("Could not verify SQL content")
        
        logger.info("Backup verification completed")


def main():
    """Main backup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database backup and restore utility')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create database backup')
    backup_parser.add_argument('--name', help='Backup name (default: timestamp)')
    backup_parser.add_argument('--no-compress', action='store_true', help='Do not compress backup')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore database from backup')
    restore_parser.add_argument('backup_file', help='Backup file to restore')
    restore_parser.add_argument('--drop', action='store_true', help='Drop existing database before restore')
    
    # List command
    subparsers.add_parser('list', help='List available backups')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove old backup files')
    cleanup_parser.add_argument('--keep', type=int, default=10, help='Number of backups to keep')
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify backup file integrity')
    verify_parser.add_argument('backup_file', help='Backup file to verify')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        backup_util = DatabaseBackup()
        
        if args.command == 'backup':
            backup_file = backup_util.create_backup(
                backup_name=args.name,
                compress=not args.no_compress
            )
            logger.info(f"Backup completed: {backup_file}")
            
        elif args.command == 'restore':
            backup_util.restore_backup(args.backup_file, drop_existing=args.drop)
            
        elif args.command == 'list':
            backup_util.list_backups()
            
        elif args.command == 'cleanup':
            backup_util.cleanup_old_backups(keep_count=args.keep)
            
        elif args.command == 'verify':
            backup_util.verify_backup(args.backup_file)
            
    except BackupError as e:
        logger.error(f"Backup operation failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()