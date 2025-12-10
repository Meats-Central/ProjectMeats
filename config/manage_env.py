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
        """
        # 1. Explicit Mapping (e.g., SSH_PASSWORD for UAT)
        if "ci_secret_mapping" in var_def:
            if env_name in var_def["ci_secret_mapping"]:
                return var_def["ci_secret_mapping"][env_name]
        
        # 2. Pattern Mapping (e.g., {PREFIX}_DB_HOST)
        env_config = self.environments[env_name]
        prefix = env_config.get("prefix", "DEV") # Default to DEV if missing
        
        pattern = var_def.get("ci_secret_pattern")
        if pattern:
            return pattern.replace("{PREFIX}", prefix)
            
        return f"{prefix}_{var_name}" # Ultimate fallback

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
            categories = ["infrastructure"] # Infra is needed for all
            if env_type == "backend":
                categories.append("application")
            elif env_type == "frontend":
                categories.append("frontend_runtime")

            for category in categories:
                vars_in_cat = self.variables.get(category, {})
                for var_name, var_def in vars_in_cat.items():
                    # Calculate expected secret name
                    secret_name = self._resolve_secret_name(env_name, var_name, var_def)
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

def main():
    parser = argparse.ArgumentParser(description="Environment & Secret Manager")
    parser.add_argument("command", choices=["audit"], help="Command to run")
    args = parser.parse_args()

    manager = EnvironmentManager()
    
    if args.command == "audit":
        manager.audit_secrets()

if __name__ == "__main__":
    main()