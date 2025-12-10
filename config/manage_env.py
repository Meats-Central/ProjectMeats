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

    def audit_secrets(self):
        print(f"{Colors.BOLD}Starting Environment-Aware Audit (Manifest v{self.manifest.get('version', '?.?')})...{Colors.END}\n")
        
        # 1. Fetch Global Secrets (Available to all)
        global_secrets = self._get_secrets(None)
        print(f"{Colors.CYAN}✓ Fetched {len(global_secrets)} Global Repository Secrets{Colors.END}")

        all_required_secrets = set()
        has_missing = False

        # 2. Audit Each Environment
        for env_name, env_config in self.environments.items():
            print(f"\nScanning Environment: {Colors.BOLD}{env_name}{Colors.END}...")
            
            # Fetch Env-Specific Secrets
            env_secrets = self._get_secrets(env_name)
            # Effective access = Env Secrets + Global Secrets
            available_secrets = env_secrets.union(global_secrets)
            
            missing_in_this_env = []
            env_type = env_config.get("type", "backend")
            
            categories = ["infrastructure"]
            if env_type == "backend":
                categories.append("application")
            elif env_type == "frontend":
                categories.append("frontend_runtime")

            for category in categories:
                vars_in_cat = self.variables.get(category, {})
                for var_name, var_def in vars_in_cat.items():
                    secret_name = self._resolve_secret_name(env_name, var_name, var_def)
                    
                    # Track for Zombie check (only if strictly required, simplified logic here)
                    # Note: We technically can't track "all required" globally easily because of overlaps,
                    # but we can track what we looked for.
                    
                    if secret_name not in available_secrets:
                        missing_in_this_env.append(f"{var_name} -> {secret_name}")

            if missing_in_this_env:
                has_missing = True
                print(f"{Colors.RED}  ❌ MISSING:{Colors.END}")
                for item in missing_in_this_env:
                    print(f"     - {item}")
            else:
                print(f"{Colors.GREEN}  ✅ All Clear ({len(env_secrets)} env-specific secrets found){Colors.END}")

        # 3. Zombie Report (Global Only)
        # It's hard to definitively call an Environment secret a zombie without querying ALL envs perfectly,
        # so we focus on Global Zombies which are most dangerous/confusing.
        print(f"\n{Colors.BOLD}--- GLOBAL ZOMBIE SECRETS (Repo-level, potentially unused) ---{Colors.END}")
        # A simple heuristic: If it's in global but looks like a specific env secret (e.g. DEV_DB_HOST), warn.
        # For now, just listing globals that might be superseded by env secrets is complex.
        # We will list globals that definitely don't match our naming conventions? 
        # Let's just print the count to be safe, or skip zombie check to avoid false positives in this version.
        # User asked for accuracy on "Missing", so let's focus on that.
        
        if has_missing:
            print(f"\n{Colors.RED}Audit Failed: Required secrets are missing from their environments.{Colors.END}")
            sys.exit(1)
        else:
            print(f"\n{Colors.GREEN}Audit Passed: All environments have access to required secrets.{Colors.END}")

def main():
    parser = argparse.ArgumentParser(description="Environment & Secret Manager")
    parser.add_argument("command", choices=["audit"], help="Command to run")
    args = parser.parse_args()

    manager = EnvironmentManager()
    if args.command == "audit":
        manager.audit_secrets()

if __name__ == "__main__":
    main()
