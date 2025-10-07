#!/usr/bin/env python3
"""
E2E tests for environment management flows.

Tests cover:
- Environment validation
- Environment setup for dev/staging/prod
- Secret generation
"""
import os
import sys
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from manage_env import EnvironmentManager


class EnvironmentValidationTests(unittest.TestCase):
    """Test cases for environment validation."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.manager = EnvironmentManager()
        
        # Save original paths
        self.orig_project_root = self.manager.project_root
        self.orig_config_dir = self.manager.config_dir
        self.orig_backend_dir = self.manager.backend_dir
        self.orig_frontend_dir = self.manager.frontend_dir
        
        # Override with test directories
        self.manager.project_root = Path(self.test_dir)
        self.manager.config_dir = Path(self.test_dir) / 'config'
        self.manager.backend_dir = Path(self.test_dir) / 'backend'
        self.manager.frontend_dir = Path(self.test_dir) / 'frontend'
        
        # Create test directories
        self.manager.config_dir.mkdir(parents=True)
        self.manager.backend_dir.mkdir(parents=True)
        self.manager.frontend_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Restore original paths
        self.manager.project_root = self.orig_project_root
        self.manager.config_dir = self.orig_config_dir
        self.manager.backend_dir = self.orig_backend_dir
        self.manager.frontend_dir = self.orig_frontend_dir

    def test_validate_environment_missing_file(self):
        """Test validation fails when environment file is missing."""
        env_file = self.manager.backend_dir / '.env'
        result = self.manager.validate_environment(env_file, ['SECRET_KEY'])
        
        self.assertFalse(result)

    def test_validate_environment_missing_vars(self):
        """Test validation fails when required variables are missing."""
        env_file = self.manager.backend_dir / '.env'
        env_file.write_text('DEBUG=True\n')
        
        result = self.manager.validate_environment(
            env_file, 
            ['SECRET_KEY', 'DATABASE_URL']
        )
        
        self.assertFalse(result)

    def test_validate_environment_empty_required_var(self):
        """Test validation warns but succeeds when required variable is empty."""
        env_file = self.manager.backend_dir / '.env'
        env_file.write_text('SECRET_KEY=\nDEBUG=True\n')
        
        result = self.manager.validate_environment(
            env_file,
            ['SECRET_KEY', 'DEBUG']
        )
        
        # Empty variables produce a warning but don't fail validation
        self.assertTrue(result)

    def test_validate_environment_success(self):
        """Test validation succeeds with all required variables."""
        env_file = self.manager.backend_dir / '.env'
        env_file.write_text('SECRET_KEY=test123\nDEBUG=True\n')
        
        result = self.manager.validate_environment(
            env_file,
            ['SECRET_KEY', 'DEBUG']
        )
        
        self.assertTrue(result)


class SecretGenerationTests(unittest.TestCase):
    """Test cases for secret generation."""

    def setUp(self):
        """Set up test environment."""
        self.manager = EnvironmentManager()

    def test_generate_secret_key_length(self):
        """Test that generated secret key has correct length."""
        secret = self.manager.generate_secret_key()
        
        self.assertEqual(len(secret), 50)

    def test_generate_secret_key_uniqueness(self):
        """Test that generated secret keys are unique."""
        secret1 = self.manager.generate_secret_key()
        secret2 = self.manager.generate_secret_key()
        
        self.assertNotEqual(secret1, secret2)

    def test_generate_secret_key_characters(self):
        """Test that generated secret key contains valid characters."""
        import string
        secret = self.manager.generate_secret_key()
        
        valid_chars = set(string.ascii_letters + string.digits + '!@#$%^&*')
        secret_chars = set(secret)
        
        self.assertTrue(secret_chars.issubset(valid_chars))


class EnvironmentSetupTests(unittest.TestCase):
    """Test cases for environment setup."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.manager = EnvironmentManager()
        
        # Save original paths
        self.orig_project_root = self.manager.project_root
        self.orig_config_dir = self.manager.config_dir
        self.orig_backend_dir = self.manager.backend_dir
        self.orig_frontend_dir = self.manager.frontend_dir
        
        # Override with test directories
        self.manager.project_root = Path(self.test_dir)
        self.manager.config_dir = Path(self.test_dir) / 'config'
        self.manager.backend_dir = Path(self.test_dir) / 'backend'
        self.manager.frontend_dir = Path(self.test_dir) / 'frontend'
        
        # Create test directories
        self.manager.config_dir.mkdir(parents=True)
        self.manager.backend_dir.mkdir(parents=True)
        self.manager.frontend_dir.mkdir(parents=True)
        
        # Create template directories
        (self.manager.config_dir / 'environments').mkdir()
        (self.manager.config_dir / 'shared').mkdir()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Restore original paths
        self.manager.project_root = self.orig_project_root
        self.manager.config_dir = self.orig_config_dir
        self.manager.backend_dir = self.orig_backend_dir
        self.manager.frontend_dir = self.orig_frontend_dir

    def test_required_backend_vars_defined(self):
        """Test that required backend variables are defined."""
        required_vars = self.manager.required_backend_vars
        
        self.assertIn('SECRET_KEY', required_vars)
        self.assertIn('DEBUG', required_vars)
        self.assertIn('ALLOWED_HOSTS', required_vars)
        self.assertIn('DATABASE_URL', required_vars)
        self.assertIn('CORS_ALLOWED_ORIGINS', required_vars)

    def test_required_frontend_vars_defined(self):
        """Test that required frontend variables are defined."""
        required_vars = self.manager.required_frontend_vars
        
        self.assertIn('REACT_APP_API_BASE_URL', required_vars)
        self.assertIn('REACT_APP_ENVIRONMENT', required_vars)
        self.assertIn('REACT_APP_AI_ASSISTANT_ENABLED', required_vars)

    def test_optional_backend_vars_defined(self):
        """Test that optional backend variables are defined."""
        optional_vars = self.manager.optional_backend_vars
        
        self.assertIn('OPENAI_API_KEY', optional_vars)
        self.assertIn('ANTHROPIC_API_KEY', optional_vars)


class EnvironmentConfigurationTests(unittest.TestCase):
    """Test cases for environment configuration structure."""

    def setUp(self):
        """Set up test environment."""
        self.manager = EnvironmentManager()

    def test_environment_manager_initialization(self):
        """Test that EnvironmentManager initializes correctly."""
        self.assertIsNotNone(self.manager.project_root)
        self.assertIsNotNone(self.manager.config_dir)
        self.assertIsNotNone(self.manager.backend_dir)
        self.assertIsNotNone(self.manager.frontend_dir)

    def test_required_variables_not_empty(self):
        """Test that required variables lists are not empty."""
        self.assertGreater(len(self.manager.required_backend_vars), 0)
        self.assertGreater(len(self.manager.required_frontend_vars), 0)

    def test_log_method_exists(self):
        """Test that log method exists and is callable."""
        self.assertTrue(callable(self.manager.log))


class IntegrationTests(unittest.TestCase):
    """Integration tests for environment management workflows."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.manager = EnvironmentManager()
        
        # Override with test directories
        self.manager.project_root = Path(self.test_dir)
        self.manager.config_dir = Path(self.test_dir) / 'config'
        self.manager.backend_dir = Path(self.test_dir) / 'backend'
        self.manager.frontend_dir = Path(self.test_dir) / 'frontend'
        
        # Create test directories
        self.manager.config_dir.mkdir(parents=True)
        self.manager.backend_dir.mkdir(parents=True)
        self.manager.frontend_dir.mkdir(parents=True)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_validate_then_generate_secret(self):
        """Test workflow: validate fails, then generate secret and validate succeeds."""
        env_file = self.manager.backend_dir / '.env'
        
        # Initial validation should fail (no file)
        result = self.manager.validate_environment(env_file, ['SECRET_KEY'])
        self.assertFalse(result)
        
        # Generate secret and create file
        secret = self.manager.generate_secret_key()
        env_file.write_text(f'SECRET_KEY={secret}\n')
        
        # Validation should now succeed
        result = self.manager.validate_environment(env_file, ['SECRET_KEY'])
        self.assertTrue(result)

    def test_multiple_environment_files(self):
        """Test managing multiple environment files."""
        backend_env = self.manager.backend_dir / '.env'
        frontend_env = self.manager.frontend_dir / '.env.local'
        
        # Create both files
        backend_env.write_text('SECRET_KEY=test123\nDEBUG=True\n')
        frontend_env.write_text('REACT_APP_API_BASE_URL=http://localhost:8000\n')
        
        # Validate both
        backend_valid = self.manager.validate_environment(
            backend_env,
            ['SECRET_KEY', 'DEBUG']
        )
        frontend_valid = self.manager.validate_environment(
            frontend_env,
            ['REACT_APP_API_BASE_URL']
        )
        
        self.assertTrue(backend_valid)
        self.assertTrue(frontend_valid)


if __name__ == '__main__':
    unittest.main()
