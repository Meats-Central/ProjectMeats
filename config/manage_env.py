#!/usr/bin/env python3
"""
ProjectMeats Environment & Secret Manager (v4.0 - Environment-Aware)
Source of Truth: config/env.manifest.json

Features:
- Audit: Environment-aware secret checking (Global + Environment Secrets)
- Logic: Available Secrets = Environment Secrets + Global Secrets
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

    def _get_secrets(self, env_name: str = None) -> Set[str]:
        """
        Fetch secrets. 
        If env_name is None, fetches Global Repository Secrets.
        If env_name is provided, fetches Environment Secrets.
        """
        cmd = ["gh", "secret", "list", "--json", "name", "-q", ".[].name"]
        if env_name:
            cmd.extend(["--env", env_name])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return set(filter(None, result.stdout.strip().split('\n')))
        except subprocess.CalledProcessError:
            # Environment might not exist or have no secrets yet
            return set()
        except FileNotFoundError:
            print(f"{Colors.RED}Error: GitHub CLI ('gh') is not installed.{Colors.END}")
            sys.exit(1)

    def _resolve_secret_name(self, env_name: str, var_name: str, var_def: Dict) -> str:
        """Determines the expected GitHub Secret name."""
        # 1. Explicit Mapping
        if "ci_secret_mapping" in var_def:
            if env_name in var_def["ci_secret_mapping"]:
                return var_def["ci_secret_mapping"][env_name]
        
        # 2. Pattern Mapping
        env_config = self.environments[env_name]
        prefix = env_config.get("prefix", "DEV")
        
        pattern = var_def.get("ci_secret_pattern")
        if pattern:
            return pattern.replace("{PREFIX}", prefix)
            
        return f"{prefix}_{var_name}"

    def audit_secrets(self, exit_on_error: bool = True):
        """
        Comprehensive audit of GitHub Secrets against manifest requirements.
        
        Args:
            exit_on_error: If True, exits with code 1 on missing secrets. 
                          If False, returns audit results for programmatic use.
        
        Returns:
            dict: Audit results with structure:
                {
                    'passed': bool,
                    'global_secrets': set,
                    'environments': {
                        'env-name': {
                            'env_secrets': set,
                            'available_secrets': set,
                            'missing': list,
                            'required': list
                        }
                    }
                }
        """
        print(f"{Colors.BOLD}Starting Environment-Aware Audit (Manifest v{self.manifest.get('version', '?.?')})...{Colors.END}\n")
        
        # 1. Fetch Global Secrets (Available to all)
        global_secrets = self._get_secrets(None)
        print(f"{Colors.CYAN}✓ Fetched {len(global_secrets)} Global Repository Secrets{Colors.END}")
        
        if global_secrets:
            print(f"{Colors.CYAN}  Global Secrets:{Colors.END}")
            for secret in sorted(global_secrets):
                print(f"    - {secret}")

        audit_results = {
            'passed': True,
            'global_secrets': global_secrets,
            'environments': {}
        }
        
        has_missing = False
        all_missing_secrets = []

        # 2. Audit Each Environment
        for env_name, env_config in self.environments.items():
            print(f"\n{Colors.BOLD}Environment: {env_name}{Colors.END}")
            print(f"  Type: {env_config.get('type', 'backend')}")
            print(f"  Prefix: {env_config.get('prefix', 'N/A')}")
            
            # Fetch Env-Specific Secrets
            env_secrets = self._get_secrets(env_name)
            # Effective access = Env Secrets + Global Secrets
            available_secrets = env_secrets.union(global_secrets)
            
            missing_in_this_env = []
            required_in_this_env = []
            env_type = env_config.get("type", "backend")
            
            categories = ["infrastructure"]
            if env_type == "backend":
                categories.append("application")
            elif env_type == "frontend":
                categories.append("frontend_runtime")

            print(f"  Checking categories: {', '.join(categories)}")
            
            for category in categories:
                vars_in_cat = self.variables.get(category, {})
                for var_name, var_def in vars_in_cat.items():
                    # Skip if value comes from config (not a secret)
                    if var_def.get("value_source") == "environment_config":
                        continue
                    
                    secret_name = self._resolve_secret_name(env_name, var_name, var_def)
                    required_in_this_env.append(secret_name)
                    
                    if secret_name not in available_secrets:
                        missing_entry = {
                            'var_name': var_name,
                            'secret_name': secret_name,
                            'category': category,
                            'environment': env_name
                        }
                        missing_in_this_env.append(missing_entry)
                        all_missing_secrets.append(missing_entry)

            # Store results for this environment
            audit_results['environments'][env_name] = {
                'env_secrets': env_secrets,
                'available_secrets': available_secrets,
                'missing': missing_in_this_env,
                'required': required_in_this_env
            }

            if missing_in_this_env:
                has_missing = True
                audit_results['passed'] = False
                print(f"\n  {Colors.RED}❌ MISSING SECRETS ({len(missing_in_this_env)}):{Colors.END}")
                for item in missing_in_this_env:
                    print(f"     {Colors.RED}•{Colors.END} {item['var_name']} → {Colors.BOLD}{item['secret_name']}{Colors.END}")
                    print(f"       Category: {item['category']}")
            else:
                print(f"\n  {Colors.GREEN}✅ All Required Secrets Present{Colors.END}")
                print(f"     Environment-specific: {len(env_secrets)}")
                print(f"     Total available: {len(available_secrets)}")

        # 3. Summary Report
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}AUDIT SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
        
        if has_missing:
            print(f"\n{Colors.RED}❌ AUDIT FAILED{Colors.END}")
            print(f"\n{Colors.RED}Total Missing Secrets: {len(all_missing_secrets)}{Colors.END}\n")
            
            # Group by environment for clarity
            for env_name, env_results in audit_results['environments'].items():
                if env_results['missing']:
                    print(f"{Colors.BOLD}{env_name}:{Colors.END}")
                    for item in env_results['missing']:
                        print(f"  • {Colors.BOLD}{item['secret_name']}{Colors.END}")
                    print()
            
            print(f"{Colors.YELLOW}ACTION REQUIRED:{Colors.END}")
            print(f"  1. Add missing secrets to GitHub:")
            print(f"     {Colors.CYAN}https://github.com/Meats-Central/ProjectMeats/settings/secrets/actions{Colors.END}")
            print(f"  2. Ensure secrets are added to the correct environment scope")
            print(f"  3. Re-run audit: {Colors.CYAN}python config/manage_env.py audit{Colors.END}\n")
            
            if exit_on_error:
                sys.exit(1)
        else:
            print(f"\n{Colors.GREEN}✅ AUDIT PASSED{Colors.END}")
            print(f"\nAll required secrets are properly configured:")
            for env_name, env_results in audit_results['environments'].items():
                print(f"  • {env_name}: {len(env_results['required'])} secrets validated")
            print()
        
        return audit_results

def main():
    parser = argparse.ArgumentParser(description="Environment & Secret Manager")
    parser.add_argument("command", choices=["audit"], help="Command to run")
    args = parser.parse_args()

    manager = EnvironmentManager()
    if args.command == "audit":
        manager.audit_secrets()

if __name__ == "__main__":
    main()
