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
    python config/manage_env.py audit
"""

import os
import sys
import shutil
import secrets
import string
import argparse
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set


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
        self.manifest_path = self.config_dir / 'env.manifest.json'
        
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
    
    def load_manifest(self) -> Optional[Dict]:
        """Load the environment manifest JSON"""
        if not self.manifest_path.exists():
            self.log(f"Manifest not found: {self.manifest_path}", "ERROR")
            return None
        
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON in manifest: {e}", "ERROR")
            return None
    
    def get_github_secrets(self) -> Optional[Set[str]]:
        """Retrieve all GitHub secrets using gh CLI"""
        try:
            result = subprocess.run(
                ['gh', 'secret', 'list', '--json', 'name'],
                capture_output=True,
                text=True,
                check=True
            )
            secrets_data = json.loads(result.stdout)
            return {secret['name'] for secret in secrets_data}
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to retrieve GitHub secrets: {e.stderr}", "ERROR")
            return None
        except FileNotFoundError:
            self.log("GitHub CLI (gh) not found. Install it to use audit feature.", "ERROR")
            self.log("Visit: https://cli.github.com/", "INFO")
            return None
        except json.JSONDecodeError as e:
            self.log(f"Failed to parse GitHub secrets response: {e}", "ERROR")
            return None
    
    def extract_manifest_secrets(self, manifest: Dict) -> Set[str]:
        """Extract all expected secret names from the manifest"""
        expected_secrets = set()
        
        variables = manifest.get('variables', {})
        environments = manifest.get('environments', {})
        
        for category in variables.values():
            for var_name, var_config in category.items():
                # Handle explicit mappings
                if 'ci_secret_mapping' in var_config:
                    for env_name, secret_name in var_config['ci_secret_mapping'].items():
                        expected_secrets.add(secret_name)
                
                # Handle pattern-based secrets
                if 'ci_secret_pattern' in var_config:
                    pattern = var_config['ci_secret_pattern']
                    for env_name, env_config in environments.items():
                        if 'prefix' in env_config:
                            secret_name = pattern.replace('{PREFIX}', env_config['prefix'])
                            expected_secrets.add(secret_name)
        
        return expected_secrets
    
    def audit_secrets(self) -> bool:
        """Audit GitHub secrets against manifest"""
        self.log("=" * 70, "INFO")
        self.log("🔍 ENVIRONMENT MANIFEST AUDIT", "INFO")
        self.log("=" * 70, "INFO")
        
        # Load manifest
        manifest = self.load_manifest()
        if not manifest:
            return False
        
        self.log(f"✓ Loaded manifest v{manifest.get('version', 'unknown')}", "SUCCESS")
        
        # Get GitHub secrets
        github_secrets = self.get_github_secrets()
        if github_secrets is None:
            return False
        
        self.log(f"✓ Retrieved {len(github_secrets)} secrets from GitHub", "SUCCESS")
        
        # Extract expected secrets from manifest
        expected_secrets = self.extract_manifest_secrets(manifest)
        self.log(f"✓ Extracted {len(expected_secrets)} expected secrets from manifest", "SUCCESS")
        
        # Find zombie and missing secrets
        zombie_secrets = github_secrets - expected_secrets
        missing_secrets = expected_secrets - github_secrets
        
        # Report findings
        self.log("\n" + "=" * 70, "INFO")
        
        if zombie_secrets:
            self.log("🧟 ZOMBIE SECRETS (In GitHub, NOT in manifest):", "WARNING")
            self.log("-" * 70, "WARNING")
            for secret in sorted(zombie_secrets):
                self.log(f"  • {secret}", "WARNING")
            self.log(f"\nTotal: {len(zombie_secrets)} zombie secret(s)", "WARNING")
        else:
            self.log("✅ No zombie secrets found", "SUCCESS")
        
        self.log("\n" + "=" * 70, "INFO")
        
        if missing_secrets:
            self.log("❌ MISSING SECRETS (In manifest, NOT in GitHub):", "ERROR")
            self.log("-" * 70, "ERROR")
            for secret in sorted(missing_secrets):
                self.log(f"  • {secret}", "ERROR")
            self.log(f"\nTotal: {len(missing_secrets)} missing secret(s)", "ERROR")
        else:
            self.log("✅ No missing secrets found", "SUCCESS")
        
        self.log("\n" + "=" * 70, "INFO")
        
        # Summary
        if not zombie_secrets and not missing_secrets:
            self.log("🎉 AUDIT PASSED: All secrets are in sync!", "SUCCESS")
            return True
        else:
            self.log("⚠️  AUDIT INCOMPLETE: Discrepancies found", "WARNING")
            if zombie_secrets:
                self.log(f"   - {len(zombie_secrets)} zombie secret(s) should be removed or added to manifest", "WARNING")
            if missing_secrets:
                self.log(f"   - {len(missing_secrets)} missing secret(s) must be added to GitHub", "WARNING")
            return False


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
  python config/manage_env.py audit
        """
    )
    
    parser.add_argument(
        'action',
        choices=['setup', 'validate', 'generate-secrets', 'audit'],
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
    
    elif args.action == 'audit':
        success = manager.audit_secrets()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()