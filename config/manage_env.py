#!/usr/bin/env python3
"""
ProjectMeats Environment & Secret Manager (v3.0)
Source of Truth: config/env.manifest.json

Features:
- Audit: Compares defined secrets in Manifest vs GitHub Repo.
- Validate: Checks local .env files against Manifest requirements.
- Reporting: Explicitly names the environment (e.g. 'uat2-frontend') for every error.
"""

import json
import subprocess
import sys
import argparse
from pathlib import Path
from typing import Dict, Set, List, Any

# --- Configuration ---
MANIFEST_PATH = Path(__file__).parent / "env.manifest.json"

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

class EnvironmentManager:
    def __init__(self):
        self.manifest = self._load_manifest()
        self.environments = self.manifest.get("environments", {})
        self.variables = self.manifest.get("variables", {})
        self.project_root = Path(__file__).parent.parent
        

    def _load_manifest(self) -> Dict[str, Any]:
        if not MANIFEST_PATH.exists():
            print(f"{Colors.RED}CRITICAL: Manifest not found at {MANIFEST_PATH}{Colors.END}")
            sys.exit(1)
        with open(MANIFEST_PATH, 'r') as f:
            return json.load(f)

    def _get_github_secrets(self) -> Set[str]:
        """Fetch list of all secret names currently in GitHub Repo"""
        print(f"{Colors.CYAN}Fetching secrets from GitHub...{Colors.END}")
        try:
            # Requires 'gh' CLI to be authenticated
            result = subprocess.run(
                ["gh", "secret", "list", "--json", "name", "-q", ".[].name"],
                capture_output=True, text=True, check=True
            )
            # Filter out empty strings if any
            return set(filter(None, result.stdout.strip().split('\n')))
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}Error fetching secrets: {e.stderr}{Colors.END}")
            print(f"{Colors.YELLOW}Tip: Run 'export GITHUB_TOKEN=...' if in Codespaces.{Colors.END}")
            sys.exit(1)
        except FileNotFoundError:
            print(f"{Colors.RED}Error: GitHub CLI ('gh') is not installed.{Colors.END}")
            sys.exit(1)

    def _resolve_secret_name(self, env_name: str, var_name: str, var_def: Dict) -> str:
        """
        Determines the GitHub Secret name for a given variable in a specific environment.
        Logic:
        1. Check 'ci_secret_mapping' for an explicit override.
        2. Fallback to 'ci_secret_pattern' replacement.
        3. Return None if variable doesn't apply to this environment.
        """
        # 1. Explicit Mapping (e.g., SSH_PASSWORD for UAT)
        if "ci_secret_mapping" in var_def:
            # Only return if this env is explicitly mapped
            return var_def["ci_secret_mapping"].get(env_name)
        
        # 2. Pattern Mapping (e.g., {PREFIX}_DB_HOST)
        pattern = var_def.get("ci_secret_pattern")
        if pattern:
            env_config = self.environments[env_name]
            prefix = env_config.get("prefix", "DEV")
            return pattern.replace("{PREFIX}", prefix)
            
        return None  # Variable doesn't apply to this environment

    def audit_secrets(self):
        """
        Compare Manifest requirements against actual GitHub Secrets.
        Reports status PER ENVIRONMENT.
        """
        print(f"{Colors.BOLD}Starting Audit (Manifest v{self.manifest.get('version', '?.?')})...{Colors.END}\n")
        
        existing_secrets = self._get_github_secrets()
        all_required_secrets = set()
        missing_by_env = {}

        # 1. Analyze Requirements
        for env_name, env_config in self.environments.items():
            missing_by_env[env_name] = []
            env_type = env_config.get("type", "backend") # backend or frontend
            
            # Iterate through relevant variable categories
            categories = []
            if env_type == "backend":
                categories = ["infrastructure", "application"]
            elif env_type == "frontend":
                categories = ["frontend_runtime"]

            for category in categories:
                vars_in_cat = self.variables.get(category, {})
                for var_name, var_def in vars_in_cat.items():
                    # Calculate expected secret name
                    secret_name = self._resolve_secret_name(env_name, var_name, var_def)
                    
                    # Skip if variable doesn't apply to this environment
                    if secret_name is None:
                        continue
                    
                    all_required_secrets.add(secret_name)
                    
                    if secret_name not in existing_secrets:
                        missing_by_env[env_name].append(f"{var_name} -> {secret_name}")

        # 2. Report Missing Secrets (The Fix for your issue)
        print(f"\n{Colors.BOLD}--- MISSING SECRETS REPORT ---{Colors.END}")
        has_missing = False
        for env_name, missing_list in missing_by_env.items():
            if missing_list:
                has_missing = True
                print(f"\n{Colors.RED}❌ Environment: {env_name}{Colors.END}")
                for item in missing_list:
                    print(f"   - {item}")
            else:
                print(f"{Colors.GREEN}✅ Environment: {env_name} is clean.{Colors.END}")

        # 3. Report Zombie Secrets
        print(f"\n{Colors.BOLD}--- ZOMBIE SECRETS (In GitHub, but not in Manifest) ---{Colors.END}")
        zombies = existing_secrets - all_required_secrets
        # Filter out GitHub default secrets if any
        zombies = {z for z in zombies if not z.startswith("GITHUB_")}
        
        if zombies:
            for z in sorted(zombies):
                print(f"{Colors.YELLOW}🧟 {z}{Colors.END}")
            print(f"\n{Colors.YELLOW}Action: Delete these using 'gh secret delete <NAME>'{Colors.END}")
        else:
            print(f"{Colors.GREEN}No zombie secrets found.{Colors.END}")

        if has_missing:
            print(f"\n{Colors.RED}Audit Failed: Missing required secrets.{Colors.END}")
            sys.exit(1)
        else:
            print(f"\n{Colors.GREEN}Audit Passed: All systems go.{Colors.END}")

    def generate_backend_env(self, env_name: str, output_path: Path = None):
        """
        Generate backend/.env file from manifest for specified environment.
        """
        if env_name not in self.environments:
            print(f"{Colors.RED}Error: Unknown environment '{env_name}'{Colors.END}")
            print(f"Available: {', '.join(self.environments.keys())}")
            sys.exit(1)
        
        env_config = self.environments[env_name]
        if env_config.get("type") != "backend":
            print(f"{Colors.RED}Error: '{env_name}' is not a backend environment{Colors.END}")
            sys.exit(1)
        
        if output_path is None:
            output_path = self.project_root / "backend" / ".env"
        
        print(f"{Colors.CYAN}Generating backend .env for {env_name}...{Colors.END}")
        
        lines = [
            f"# Generated from env.manifest.json for {env_name}",
            f"# DO NOT EDIT MANUALLY - Use manage_env.py",
            ""
        ]
        
        # Add infrastructure variables
        for var_name, var_def in self.variables.get("infrastructure", {}).items():
            secret_name = self._resolve_secret_name(env_name, var_name, var_def)
            if secret_name:
                lines.append(f"{var_name}=<{secret_name}>")
        
        # Add application variables
        for var_name, var_def in self.variables.get("application", {}).items():
            if var_def.get("value_source") == "environment_config":
                # Use value from environment config
                value = env_config.get("django_settings", "")
                lines.append(f"{var_name}={value}")
            else:
                secret_name = self._resolve_secret_name(env_name, var_name, var_def)
                if secret_name:
                    lines.append(f"{var_name}=<{secret_name}>")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines) + "\n")
        print(f"{Colors.GREEN}✅ Generated: {output_path}{Colors.END}")
        print(f"{Colors.YELLOW}Note: Replace <SECRET_NAME> placeholders with actual values{Colors.END}")

    def generate_frontend_env(self, env_name: str, output_path: Path = None):
        """
        Generate frontend/.env file from manifest for specified environment.
        """
        if env_name not in self.environments:
            print(f"{Colors.RED}Error: Unknown environment '{env_name}'{Colors.END}")
            print(f"Available: {', '.join(self.environments.keys())}")
            sys.exit(1)
        
        env_config = self.environments[env_name]
        if env_config.get("type") != "frontend":
            print(f"{Colors.RED}Error: '{env_name}' is not a frontend environment{Colors.END}")
            sys.exit(1)
        
        if output_path is None:
            output_path = self.project_root / "frontend" / ".env"
        
        print(f"{Colors.CYAN}Generating frontend .env for {env_name}...{Colors.END}")
        
        lines = [
            f"# Generated from env.manifest.json for {env_name}",
            f"# DO NOT EDIT MANUALLY - Use manage_env.py",
            ""
        ]
        
        # Add frontend runtime variables
        for var_name, var_def in self.variables.get("frontend_runtime", {}).items():
            # Check for direct values in manifest
            if "values" in var_def and env_name in var_def["values"]:
                value = var_def["values"][env_name]
                lines.append(f"{var_name}={value}")
            # Check for default value
            elif "default" in var_def:
                lines.append(f"{var_name}={var_def['default']}")
            # Fallback to secret pattern
            else:
                secret_name = self._resolve_secret_name(env_name, var_name, var_def)
                if secret_name:
                    lines.append(f"{var_name}=<{secret_name}>")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines) + "\n")
        print(f"{Colors.GREEN}✅ Generated: {output_path}{Colors.END}")


def main():
    parser = argparse.ArgumentParser(description="Environment & Secret Manager")
    parser.add_argument("command", choices=["audit", "setup"], help="Command to run")
    parser.add_argument("environment", nargs="?", help="Target environment name (e.g., dev-backend, dev-frontend)")
    parser.add_argument("--target", choices=["backend", "frontend"], help="Generate .env for backend or frontend")
    parser.add_argument("--output", type=Path, help="Custom output path for .env file")
    args = parser.parse_args()

    manager = EnvironmentManager()
    
    if args.command == "audit":
        manager.audit_secrets()
    elif args.command == "setup":
        if not args.environment:
            print(f"{Colors.RED}Error: environment argument required for setup{Colors.END}")
            print("Example: python manage_env.py setup dev-backend --target=backend")
            sys.exit(1)
        
        # Auto-detect target if not specified
        if not args.target:
            env_config = manager.environments.get(args.environment)
            if env_config:
                args.target = env_config.get("type", "backend")
            else:
                print(f"{Colors.RED}Error: Unknown environment '{args.environment}'{Colors.END}")
                sys.exit(1)
        
        if args.target == "backend":
            manager.generate_backend_env(args.environment, args.output)
        elif args.target == "frontend":
            manager.generate_frontend_env(args.environment, args.output)


if __name__ == "__main__":
    main()