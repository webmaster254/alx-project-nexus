#!/usr/bin/env python
"""
Deployment testing and validation script for job board backend.
"""

import os
import sys
import json
import time
import requests
import subprocess
import logging
from pathlib import Path
from urllib.parse import urljoin

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentTestError(Exception):
    """Custom exception for deployment test errors."""
    pass


class DeploymentTester:
    """Deployment testing and validation utility."""
    
    def __init__(self, base_url='http://localhost:8000', timeout=30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.timeout = timeout
        
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
                    cwd=PROJECT_ROOT
                )
                return result.stdout.strip()
            else:
                subprocess.run(
                    command,
                    shell=True,
                    check=check,
                    cwd=PROJECT_ROOT
                )
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed: {command}"
            if capture_output and e.stderr:
                error_msg += f"\nError: {e.stderr}"
            logger.error(error_msg)
            raise DeploymentTestError(error_msg)
    
    def wait_for_service(self, max_attempts=30, delay=2):
        """Wait for the service to become available."""
        logger.info(f"Waiting for service at {self.base_url}...")
        
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/api/health/live/")
                if response.status_code == 200:
                    logger.info("Service is available")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            logger.info(f"Attempt {attempt + 1}/{max_attempts} - Service not ready, waiting {delay}s...")
            time.sleep(delay)
        
        raise DeploymentTestError("Service did not become available within timeout")
    
    def test_health_endpoints(self):
        """Test health check endpoints."""
        logger.info("Testing health check endpoints...")
        
        endpoints = [
            '/api/health/live/',
            '/api/health/ready/',
            '/api/health/',
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    logger.info(f"✓ {endpoint} - OK")
                    if endpoint == '/api/health/':
                        # Validate detailed health response
                        data = response.json()
                        if 'status' in data and 'checks' in data:
                            logger.info(f"  Status: {data['status']}")
                            for check_name, check_data in data['checks'].items():
                                status = check_data.get('status', 'unknown')
                                logger.info(f"  {check_name}: {status}")
                        else:
                            logger.warning(f"  Invalid health response format")
                else:
                    logger.error(f"✗ {endpoint} - Status: {response.status_code}")
                    raise DeploymentTestError(f"Health check failed: {endpoint}")
            except requests.exceptions.RequestException as e:
                logger.error(f"✗ {endpoint} - Error: {e}")
                raise DeploymentTestError(f"Health check request failed: {endpoint}")
    
    def test_api_documentation(self):
        """Test API documentation endpoints."""
        logger.info("Testing API documentation...")
        
        endpoints = [
            '/api/docs/',
            '/api/schema/',
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    logger.info(f"✓ {endpoint} - OK")
                else:
                    logger.error(f"✗ {endpoint} - Status: {response.status_code}")
                    raise DeploymentTestError(f"Documentation endpoint failed: {endpoint}")
            except requests.exceptions.RequestException as e:
                logger.error(f"✗ {endpoint} - Error: {e}")
                raise DeploymentTestError(f"Documentation request failed: {endpoint}")
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints."""
        logger.info("Testing authentication endpoints...")
        
        # Test registration endpoint
        register_url = f"{self.base_url}/api/auth/register/"
        test_user_data = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        try:
            response = self.session.post(register_url, json=test_user_data)
            if response.status_code in [201, 400]:  # 400 might be validation error, which is OK
                logger.info("✓ Registration endpoint - OK")
            else:
                logger.error(f"✗ Registration endpoint - Status: {response.status_code}")
                raise DeploymentTestError("Registration endpoint failed")
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Registration endpoint - Error: {e}")
            raise DeploymentTestError("Registration request failed")
        
        # Test login endpoint structure
        login_url = f"{self.base_url}/api/auth/login/"
        try:
            # This should fail with 400 (bad request) but endpoint should exist
            response = self.session.post(login_url, json={})
            if response.status_code in [400, 401]:  # Expected for empty credentials
                logger.info("✓ Login endpoint - OK")
            else:
                logger.error(f"✗ Login endpoint - Status: {response.status_code}")
                raise DeploymentTestError("Login endpoint failed")
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Login endpoint - Error: {e}")
            raise DeploymentTestError("Login request failed")
    
    def test_api_endpoints(self):
        """Test main API endpoints."""
        logger.info("Testing main API endpoints...")
        
        endpoints = [
            ('/api/jobs/', 'GET'),
            ('/api/categories/', 'GET'),
            ('/api/industries/', 'GET'),
            ('/api/job-types/', 'GET'),
        ]
        
        for endpoint, method in endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                if method == 'GET':
                    response = self.session.get(url)
                else:
                    response = self.session.request(method, url)
                
                if response.status_code in [200, 401]:  # 401 is OK for protected endpoints
                    logger.info(f"✓ {method} {endpoint} - OK")
                else:
                    logger.error(f"✗ {method} {endpoint} - Status: {response.status_code}")
                    raise DeploymentTestError(f"API endpoint failed: {method} {endpoint}")
            except requests.exceptions.RequestException as e:
                logger.error(f"✗ {method} {endpoint} - Error: {e}")
                raise DeploymentTestError(f"API request failed: {method} {endpoint}")
    
    def test_database_connectivity(self):
        """Test database connectivity through Django management command."""
        logger.info("Testing database connectivity...")
        
        try:
            settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'config.settings.production')
            self.run_command(
                f"python manage.py check --database default --settings={settings_module}"
            )
            logger.info("✓ Database connectivity - OK")
        except DeploymentTestError:
            logger.error("✗ Database connectivity - FAILED")
            raise
    
    def test_static_files(self):
        """Test static file serving."""
        logger.info("Testing static file serving...")
        
        # Test common static file paths
        static_paths = [
            '/static/admin/css/base.css',
            '/static/rest_framework/css/bootstrap.min.css',
        ]
        
        for path in static_paths:
            url = f"{self.base_url}{path}"
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    logger.info(f"✓ Static file {path} - OK")
                else:
                    logger.warning(f"⚠ Static file {path} - Status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠ Static file {path} - Error: {e}")
    
    def test_security_headers(self):
        """Test security headers."""
        logger.info("Testing security headers...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/health/live/")
            headers = response.headers
            
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
            ]
            
            for header in security_headers:
                if header in headers:
                    logger.info(f"✓ Security header {header}: {headers[header]}")
                else:
                    logger.warning(f"⚠ Missing security header: {header}")
                    
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠ Could not test security headers: {e}")
    
    def test_performance(self):
        """Test basic performance metrics."""
        logger.info("Testing performance...")
        
        endpoints = [
            '/api/health/live/',
            '/api/jobs/',
            '/api/categories/',
        ]
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                start_time = time.time()
                response = self.session.get(url)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code == 200:
                    if response_time < 1000:  # Less than 1 second
                        logger.info(f"✓ {endpoint} - Response time: {response_time:.2f}ms")
                    else:
                        logger.warning(f"⚠ {endpoint} - Slow response: {response_time:.2f}ms")
                else:
                    logger.warning(f"⚠ {endpoint} - Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠ Performance test failed for {endpoint}: {e}")
    
    def run_all_tests(self):
        """Run all deployment tests."""
        logger.info("Starting deployment validation tests...")
        
        test_methods = [
            self.wait_for_service,
            self.test_health_endpoints,
            self.test_api_documentation,
            self.test_authentication_endpoints,
            self.test_api_endpoints,
            self.test_database_connectivity,
            self.test_static_files,
            self.test_security_headers,
            self.test_performance,
        ]
        
        passed_tests = 0
        failed_tests = 0
        
        for test_method in test_methods:
            try:
                test_method()
                passed_tests += 1
            except DeploymentTestError as e:
                logger.error(f"Test failed: {test_method.__name__} - {e}")
                failed_tests += 1
            except Exception as e:
                logger.error(f"Unexpected error in {test_method.__name__}: {e}")
                failed_tests += 1
        
        logger.info(f"\nTest Results:")
        logger.info(f"✓ Passed: {passed_tests}")
        logger.info(f"✗ Failed: {failed_tests}")
        logger.info(f"Total: {passed_tests + failed_tests}")
        
        if failed_tests > 0:
            logger.error("Some tests failed. Please check the deployment.")
            return False
        else:
            logger.info("All tests passed! Deployment is healthy.")
            return True


def main():
    """Main testing function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test deployment health and functionality')
    parser.add_argument('--url', default='http://localhost:8000',
                       help='Base URL of the deployed application')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds')
    parser.add_argument('--wait-time', type=int, default=60,
                       help='Maximum time to wait for service to start')
    
    args = parser.parse_args()
    
    tester = DeploymentTester(args.url, args.timeout)
    
    try:
        success = tester.run_all_tests()
        if success:
            logger.info("Deployment validation completed successfully!")
            sys.exit(0)
        else:
            logger.error("Deployment validation failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Deployment testing failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()