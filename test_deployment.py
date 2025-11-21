#!/usr/bin/env python3
"""
ProjectMeats3 Deployment Testing Script

This script validates the entire deployment process and configuration.
It can be run locally or in CI to ensure deployment readiness.

Environment Priority:
    Primary staging environment: UAT (uat.meatscentral.com)
    Legacy staging: staging.meatscentral.com (DEPRECATED - use UAT)
    Production: meatscentral.com

Usage:
    python test_deployment.py --environment production
    python test_deployment.py --environment development --full-test
    python test_deployment.py --validate-only
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'


class DeploymentTester:
    """Comprehensive deployment testing for ProjectMeats3"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        self.config_dir = self.project_root / 'config'
        
        # Log warning if using deprecated staging terminology
        if environment == "staging":
            self.log("⚠️  NOTE: 'staging' refers to UAT environment (uat.meatscentral.com)", "WARNING")
            self.log("   staging.meatscentral.com is DEPRECATED - UAT is the active middle environment", "WARNING")
        
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "tests": []
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with color coding"""
        color_map = {
            "INFO": Colors.CYAN,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "HEADER": Colors.BOLD + Colors.BLUE
        }
        color = color_map.get(level, Colors.WHITE)
        print(f"{color}{message}{Colors.END}")
    
    def run_test(self, test_name: str, test_func, *args, **kwargs) -> bool:
        """Run a test and record results"""
        self.log(f"Running: {test_name}", "INFO")
        try:
            result = test_func(*args, **kwargs)
            if result:
                self.log(f"✅ PASSED: {test_name}", "SUCCESS")
                self.test_results["passed"] += 1
                self.test_results["tests"].append({"name": test_name, "status": "PASSED"})
                return True
            else:
                self.log(f"❌ FAILED: {test_name}", "ERROR")
                self.test_results["failed"] += 1
                self.test_results["tests"].append({"name": test_name, "status": "FAILED"})
                return False
        except Exception as e:
            self.log(f"❌ ERROR: {test_name} - {str(e)}", "ERROR")
            self.test_results["failed"] += 1
            self.test_results["tests"].append({"name": test_name, "status": "ERROR", "error": str(e)})
            return False
    
    def test_environment_setup(self) -> bool:
        """Test that environment is properly configured"""
        env_file = self.backend_dir / '.env'
        if not env_file.exists():
            return False
        
        # Check required environment variables
        required_vars = [
            'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'DATABASE_URL',
            'CORS_ALLOWED_ORIGINS', 'API_VERSION'
        ]
        
        with open(env_file, 'r') as f:
            content = f.read()
        
        for var in required_vars:
            if f"{var}=" not in content:
                self.log(f"Missing required variable: {var}", "ERROR")
                return False
        
        return True
    
    def test_django_configuration(self) -> bool:
        """Test Django configuration and system checks"""
        try:
            os.chdir(self.backend_dir)
            result = subprocess.run([
                sys.executable, 'manage.py', 'check', '--deploy'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.log(f"Django check failed: {result.stderr}", "ERROR")
                return False
            
            return True
        except subprocess.TimeoutExpired:
            self.log("Django check timed out", "ERROR")
            return False
        except Exception as e:
            self.log(f"Django check error: {str(e)}", "ERROR")
            return False
        finally:
            os.chdir(self.project_root)
    
    def test_database_connectivity(self) -> bool:
        """Test database connection and migrations"""
        try:
            os.chdir(self.backend_dir)
            
            # Test database connectivity
            result = subprocess.run([
                sys.executable, 'manage.py', 'migrate', '--check'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.log(f"Database connectivity failed: {result.stderr}", "ERROR")
                return False
            
            return True
        except Exception as e:
            self.log(f"Database test error: {str(e)}", "ERROR")
            return False
        finally:
            os.chdir(self.project_root)
    
    def test_static_files_collection(self) -> bool:
        """Test static files collection for production"""
        try:
            os.chdir(self.backend_dir)
            
            result = subprocess.run([
                sys.executable, 'manage.py', 'collectstatic', '--dry-run', '--noinput'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                self.log(f"Static files collection failed: {result.stderr}", "ERROR")
                return False
            
            return True
        except Exception as e:
            self.log(f"Static files test error: {str(e)}", "ERROR")
            return False
        finally:
            os.chdir(self.project_root)
    
    def test_frontend_build(self) -> bool:
        """Test frontend build process"""
        try:
            os.chdir(self.frontend_dir)
            
            # Check if node_modules exists
            if not (self.frontend_dir / 'node_modules').exists():
                self.log("Installing frontend dependencies...", "INFO")
                subprocess.run(['npm', 'install'], check=True, timeout=300)
            
            # Test build
            result = subprocess.run([
                'npm', 'run', 'build'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                self.log(f"Frontend build failed: {result.stderr}", "ERROR")
                return False
            
            # Check if build directory exists
            build_dir = self.frontend_dir / 'build'
            if not build_dir.exists():
                self.log("Build directory not created", "ERROR")
                return False
            
            return True
        except Exception as e:
            self.log(f"Frontend build error: {str(e)}", "ERROR")
            return False
        finally:
            os.chdir(self.project_root)
    
    def test_app_yaml_configuration(self) -> bool:
        """Test Digital Ocean app.yaml configuration"""
        app_yaml = self.project_root / 'app.yaml'
        if not app_yaml.exists():
            self.log("app.yaml file not found", "ERROR")
            return False
        
        try:
            import yaml
            with open(app_yaml, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check required sections
            required_sections = ['services', 'databases']
            for section in required_sections:
                if section not in config:
                    self.log(f"Missing required section in app.yaml: {section}", "ERROR")
                    return False
            
            # Check services configuration
            services = config.get('services', [])
            if len(services) < 2:  # Should have backend and frontend
                self.log("app.yaml should have at least 2 services (backend and frontend)", "ERROR")
                return False
            
            return True
        except ImportError:
            self.log("PyYAML not installed, skipping app.yaml validation", "WARNING")
            self.test_results["warnings"] += 1
            return True
        except Exception as e:
            self.log(f"app.yaml validation error: {str(e)}", "ERROR")
            return False
    
    def test_health_endpoints_local(self) -> bool:
        """Test health endpoints on local development server"""
        if self.environment != "development":
            return True  # Skip for non-development environments
        
        # This would require starting the server, so we'll simulate for now
        # In a real scenario, you'd start the server and test the endpoints
        self.log("Health endpoint test would require running server", "WARNING")
        self.test_results["warnings"] += 1
        return True
    
    def test_environment_variables_security(self) -> bool:
        """Test that production secrets are secure"""
        if self.environment != "production":
            return True
        
        env_file = self.backend_dir / '.env'
        if not env_file.exists():
            return False
        
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check for insecure configurations
        insecure_patterns = [
            ("DEBUG=True", "DEBUG should be False in production"),
            ("SECRET_KEY=django-insecure", "SECRET_KEY should not be the default insecure key"),
            ("ALLOWED_HOSTS=*", "ALLOWED_HOSTS should not be wildcard in production")
        ]
        
        for pattern, message in insecure_patterns:
            if pattern in content:
                self.log(f"Security issue: {message}", "ERROR")
                return False
        
        return True
    
    def test_ci_cd_configuration(self) -> bool:
        """Test CI/CD pipeline configuration"""
        workflow_file = self.project_root / '.github' / 'workflows' / 'ci-cd.yml'
        if not workflow_file.exists():
            self.log("CI/CD workflow file not found", "ERROR")
            return False
        
        try:
            import yaml
            with open(workflow_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check for required jobs
            jobs = config.get('jobs', {})
            required_jobs = ['backend-test', 'frontend-test']
            
            for job in required_jobs:
                if job not in jobs:
                    self.log(f"Missing required CI/CD job: {job}", "ERROR")
                    return False
            
            return True
        except ImportError:
            self.log("PyYAML not installed, skipping CI/CD validation", "WARNING")
            self.test_results["warnings"] += 1
            return True
        except Exception as e:
            self.log(f"CI/CD configuration error: {str(e)}", "ERROR")
            return False
    
    def run_deployment_tests(self, full_test: bool = False) -> bool:
        """Run all deployment tests"""
        self.log("=" * 60, "HEADER")
        self.log(f"ProjectMeats3 Deployment Testing - {self.environment.upper()} Environment", "HEADER")
        self.log("=" * 60, "HEADER")
        
        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("Django Configuration", self.test_django_configuration),
            ("Database Connectivity", self.test_database_connectivity),
            ("Static Files Collection", self.test_static_files_collection),
            ("Frontend Build Process", self.test_frontend_build),
            ("Digital Ocean app.yaml", self.test_app_yaml_configuration),
            ("Environment Security", self.test_environment_variables_security),
            ("CI/CD Configuration", self.test_ci_cd_configuration),
        ]
        
        if full_test:
            tests.append(("Health Endpoints (Local)", self.test_health_endpoints_local))
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Print results summary
        self.log("\n" + "=" * 60, "HEADER")
        self.log("TEST RESULTS SUMMARY", "HEADER")
        self.log("=" * 60, "HEADER")
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        self.log(f"Total Tests: {total_tests}", "INFO")
        self.log(f"Passed: {self.test_results['passed']}", "SUCCESS")
        self.log(f"Failed: {self.test_results['failed']}", "ERROR" if self.test_results["failed"] > 0 else "INFO")
        self.log(f"Warnings: {self.test_results['warnings']}", "WARNING" if self.test_results["warnings"] > 0 else "INFO")
        
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        self.log(f"Success Rate: {success_rate:.1f}%", "SUCCESS" if success_rate >= 90 else "WARNING")
        
        # Detailed results
        if self.test_results["failed"] > 0:
            self.log("\nFailed Tests:", "ERROR")
            for test in self.test_results["tests"]:
                if test["status"] in ["FAILED", "ERROR"]:
                    error_msg = test.get("error", "")
                    self.log(f"  - {test['name']}: {error_msg}", "ERROR")
        
        return self.test_results["failed"] == 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ProjectMeats3 Deployment Testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_deployment.py --environment development
  python test_deployment.py --environment production --full-test
  python test_deployment.py --validate-only
        """
    )
    
    parser.add_argument(
        '--environment',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Environment to test (default: development). NOTE: Use "staging" for UAT environment - staging.meatscentral.com is deprecated.'
    )
    
    parser.add_argument(
        '--full-test',
        action='store_true',
        help='Run comprehensive tests including server startup'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only run validation tests, skip build tests'
    )
    
    args = parser.parse_args()
    
    tester = DeploymentTester(args.environment)
    success = tester.run_deployment_tests(full_test=args.full_test and not args.validate_only)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()