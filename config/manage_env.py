#!/usr/bin/env python3
"""
ProjectMeats Environment Configuration Manager

This script manages environment configurations for different deployment environments.
It provides validation, setup, and deployment utilities.

Usage:
    python config/manage_env.py setup development
    python config/manage_env.py setup staging  
    python config/manage_env.py setup production
    python config/manage_env.py validate
    python config/manage_env.py generate-secrets
"""

import os
import sys
import shutil
import secrets
import string
import argparse
from pathlib import Path
from typing import Dict, List, Optional


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


class EnvironmentManager:
    """Manages ProjectMeats environment configurations"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / 'config'
        self.backend_dir = self.project_root / 'backend'
        self.frontend_dir = self.project_root / 'frontend'
        
        # Required environment variables for each component
        self.required_backend_vars = [
            'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'DATABASE_URL',
            'CORS_ALLOWED_ORIGINS', 'API_VERSION'
        ]
        
        # Optional backend variables that can be empty
        self.optional_backend_vars = [
            'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'EMAIL_HOST',
            'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD'
        ]
        
        self.required_frontend_vars = [
            'REACT_APP_API_BASE_URL', 'REACT_APP_ENVIRONMENT',
            'REACT_APP_AI_ASSISTANT_ENABLED'
        ]
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with color coding"""
        color_map = {
            "INFO": Colors.CYAN,
            "SUCCESS": Colors.GREEN, 
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED
        }
        color = color_map.get(level, Colors.WHITE)
        print(f"{color}{message}{Colors.END}")
    
    def generate_secret_key(self) -> str:
        """Generate a secure Django secret key"""
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
        return ''.join(secrets.choice(alphabet) for _ in range(50))
    
    def validate_environment(self, env_file: Path, required_vars: List[str]) -> bool:
        """Validate that all required variables are present"""
        if not env_file.exists():
            self.log(f"Environment file not found: {env_file}", "ERROR")
            return False
        
        with open(env_file, 'r') as f:
            content = f.read()
        
        missing_vars = []
        empty_required_vars = []
        
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
            else:
                # Check if required variable is empty
                lines = content.split('\n')
                for line in lines:
                    if line.startswith(f"{var}=") and not line.startswith(f"{var}=#"):
                        value = line.split('=', 1)[1].strip()
                        if not value or value == '""' or value == "''":
                            empty_required_vars.append(var)
                        break
        
        if missing_vars:
            self.log(f"Missing variables in {env_file.name}: {', '.join(missing_vars)}", "ERROR")
            return False
        
        if empty_required_vars:
            self.log(f"Empty required variables in {env_file.name}: {', '.join(empty_required_vars)}", "WARNING")
            # Don't fail for empty variables, just warn
        
        return True
    
    def setup_environment(self, environment: str) -> bool:
        """Set up environment configuration for the specified environment"""
        self.log(f"Setting up {environment} environment...", "INFO")
        
        # Backend setup
        backend_env_source = self.config_dir / 'environments' / f'{environment}.env'
        backend_env_dest = self.backend_dir / '.env'
        
        if not backend_env_source.exists():
            self.log(f"Environment configuration not found: {backend_env_source}", "ERROR")
            return False
        
        # Copy backend environment file
        if backend_env_dest.exists():
            backup_file = backend_env_dest.with_suffix('.env.backup')
            shutil.copy2(backend_env_dest, backup_file)
            self.log(f"Backed up existing .env to {backup_file.name}", "WARNING")
        
        shutil.copy2(backend_env_source, backend_env_dest)
        self.log(f"✓ Backend environment configured from {backend_env_source.name}", "SUCCESS")
        
        # Frontend setup
        frontend_template = self.config_dir / 'shared' / 'frontend.env.template'
        frontend_env_dest = self.frontend_dir / '.env.local'
        
        if frontend_template.exists():
            if frontend_env_dest.exists():
                backup_file = frontend_env_dest.with_suffix('.env.local.backup')
                shutil.copy2(frontend_env_dest, backup_file)
                self.log(f"Backed up existing .env.local to {backup_file.name}", "WARNING")
            
            shutil.copy2(frontend_template, frontend_env_dest)
            self.log(f"✓ Frontend environment template copied", "SUCCESS")
        
        # Validate setup
        self.log("Validating configuration...", "INFO")
        backend_valid = self.validate_environment(backend_env_dest, self.required_backend_vars)
        frontend_valid = self.validate_environment(frontend_env_dest, self.required_frontend_vars)
        
        if backend_valid and frontend_valid:
            self.log(f"✅ {environment.title()} environment setup complete!", "SUCCESS")
            return True
        else:
            self.log(f"❌ Environment setup completed with validation errors", "ERROR")
            return False
    
    def validate_all_environments(self) -> bool:
        """Validate all environment configurations"""
        self.log("Validating environment configurations...", "INFO")
        
        valid = True
        
        # Check backend
        backend_env = self.backend_dir / '.env'
        if not self.validate_environment(backend_env, self.required_backend_vars):
            valid = False
        
        # Check frontend  
        frontend_env = self.frontend_dir / '.env.local'
        if not self.validate_environment(frontend_env, self.required_frontend_vars):
            valid = False
        
        if valid:
            self.log("✅ All environment configurations are valid!", "SUCCESS")
        else:
            self.log("❌ Environment validation failed", "ERROR")
        
        return valid
    
    def generate_secrets(self) -> None:
        """Generate secure secrets for all environments"""
        self.log("Generating secure secrets...", "INFO")
        
        environments = ['development', 'staging', 'production']
        
        for env in environments:
            secret_key = self.generate_secret_key()
            self.log(f"{env.upper()}_SECRET_KEY={secret_key}", "INFO")
        
        self.log("\n" + "="*60, "INFO")
        self.log("IMPORTANT: Store these secrets securely!", "WARNING")
        self.log("- Add them to your environment variable management system", "WARNING")
        self.log("- Never commit them to version control", "WARNING")
        self.log("- Use different secrets for each environment", "WARNING")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ProjectMeats Environment Configuration Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python config/manage_env.py setup development
  python config/manage_env.py setup staging
  python config/manage_env.py setup production
  python config/manage_env.py validate
  python config/manage_env.py generate-secrets
        """
    )
    
    parser.add_argument(
        'action',
        choices=['setup', 'validate', 'generate-secrets'],
        help='Action to perform'
    )
    
    parser.add_argument(
        'environment',
        nargs='?',
        choices=['development', 'staging', 'production'],
        help='Environment to set up (required for setup action)'
    )
    
    args = parser.parse_args()
    
    manager = EnvironmentManager()
    
    if args.action == 'setup':
        if not args.environment:
            parser.error("Environment is required for setup action")
        success = manager.setup_environment(args.environment)
        sys.exit(0 if success else 1)
    
    elif args.action == 'validate':
        success = manager.validate_all_environments()
        sys.exit(0 if success else 1)
    
    elif args.action == 'generate-secrets':
        manager.generate_secrets()
        sys.exit(0)


if __name__ == '__main__':
    main()