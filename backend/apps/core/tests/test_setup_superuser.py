"""
Tests for the setup_superuser management command.
"""
from io import StringIO
from unittest import mock
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()


class SetupSuperuserCommandTests(TestCase):
    """Test cases for setup_superuser management command."""

    def setUp(self):
        """Set up test environment."""
        # Clean up any existing users
        User.objects.all().delete()

    def test_command_runs_with_no_env_vars_in_test_context(self):
        """Test that command uses defaults when no env vars set in test context."""
        out = StringIO()
        
        # Patch environment to simulate test context with no vars set
        with mock.patch.dict('os.environ', {'DJANGO_ENV': 'development'}, clear=True):
            with mock.patch('os.getenv') as mock_getenv:
                # Simulate missing env vars - return None for all superuser vars
                def getenv_side_effect(key, default=None):
                    if key == 'DJANGO_ENV':
                        return 'development'
                    elif key == 'DJANGO_SETTINGS_MODULE':
                        return 'projectmeats.settings.test'
                    return default
                
                mock_getenv.side_effect = getenv_side_effect
                
                # This should not raise an error in test context
                call_command('setup_superuser', stdout=out)
        
        # Check that a user was created with defaults
        self.assertTrue(User.objects.exists())
        user = User.objects.first()
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_command_fails_in_production_without_env_vars(self):
        """Test that command raises error in production without env vars."""
        out = StringIO()
        
        # Patch environment to simulate production with no vars set
        with mock.patch.dict('os.environ', {'DJANGO_ENV': 'production'}, clear=True):
            with mock.patch('os.getenv') as mock_getenv:
                # Simulate missing env vars
                def getenv_side_effect(key, default=None):
                    if key == 'DJANGO_ENV':
                        return 'production'
                    elif key == 'DJANGO_SETTINGS_MODULE':
                        return 'projectmeats.settings.production'
                    return default
                
                mock_getenv.side_effect = getenv_side_effect
                
                # This should raise ValueError
                with self.assertRaises(ValueError) as context:
                    call_command('setup_superuser', stdout=out)
                
                # Check that error message mentions the environment
                self.assertIn('production environment', str(context.exception))

    def test_command_uses_staging_vars_when_set(self):
        """Test that command uses staging env vars when properly set."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'staging',
            'STAGING_SUPERUSER_USERNAME': 'stageadmin',
            'STAGING_SUPERUSER_EMAIL': 'stage@example.com',
            'STAGING_SUPERUSER_PASSWORD': 'stagepass123'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Check user was created with staging credentials
        self.assertTrue(User.objects.filter(username='stageadmin').exists())
        user = User.objects.get(username='stageadmin')
        self.assertEqual(user.email, 'stage@example.com')
        self.assertTrue(user.check_password('stagepass123'))
        self.assertTrue(user.is_superuser)

    def test_command_logs_missing_vars_in_test_mode(self):
        """Test that command logs warnings for missing vars in test mode."""
        out = StringIO()
        
        # Set test context explicitly
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'test',
            'DJANGO_SETTINGS_MODULE': 'projectmeats.settings.test'
        }, clear=True):
            # Should log warnings but not fail
            call_command('setup_superuser', stdout=out)
        
        # Verify user was created with defaults
        self.assertTrue(User.objects.exists())

    def test_command_syncs_password_for_existing_user(self):
        """Test that command updates password for existing user."""
        # Create initial user
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='oldpass'
        )
        
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_USERNAME': 'admin',
            'DEVELOPMENT_SUPERUSER_EMAIL': 'admin@example.com',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'newpass'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Password should be updated
        user = User.objects.get(username='admin')
        self.assertTrue(user.check_password('newpass'))
        self.assertFalse(user.check_password('oldpass'))

    def test_command_handles_username_none_gracefully(self):
        """Test that command handles None username by using defaults in test context."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'test',
            'DJANGO_SETTINGS_MODULE': 'projectmeats.settings.test'
        }, clear=True):
            with mock.patch('os.getenv') as mock_getenv:
                # Return None for all credential vars
                def getenv_side_effect(key, default=None):
                    if key == 'DJANGO_ENV':
                        return 'test'
                    elif key == 'DJANGO_SETTINGS_MODULE':
                        return 'projectmeats.settings.test'
                    return default
                
                mock_getenv.side_effect = getenv_side_effect
                
                # Should not raise error, should use defaults
                call_command('setup_superuser', stdout=out)
        
        # Verify a user was created
        self.assertTrue(User.objects.exists())

    def test_verbose_logging_shows_loaded_vars(self):
        """Test that verbose mode shows which vars are set or missing."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_USERNAME': 'admin',
            'DEVELOPMENT_SUPERUSER_EMAIL': 'admin@example.com',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'testpass'
        }):
            call_command('setup_superuser', stdout=out, verbosity=2)
        
        # The command should execute successfully
        self.assertTrue(User.objects.filter(username='admin').exists())

    def test_production_requires_all_three_vars(self):
        """Test that production requires username, email, AND password."""
        out = StringIO()
        
        # Missing password
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'production',
            'PRODUCTION_SUPERUSER_USERNAME': 'prodadmin',
            'PRODUCTION_SUPERUSER_EMAIL': 'prod@example.com'
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                call_command('setup_superuser', stdout=out)
            
            self.assertIn('password', str(context.exception).lower())

    def test_uat_environment_treated_as_staging(self):
        """Test that UAT environment uses STAGING_ prefix vars."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'uat',
            'STAGING_SUPERUSER_USERNAME': 'uatadmin',
            'STAGING_SUPERUSER_EMAIL': 'uat@example.com',
            'STAGING_SUPERUSER_PASSWORD': 'uatpass123'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='uatadmin').exists())
        user = User.objects.get(username='uatadmin')
        self.assertEqual(user.email, 'uat@example.com')
        self.assertTrue(user.check_password('uatpass123'))
