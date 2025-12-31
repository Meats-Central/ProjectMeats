#!/usr/bin/env python3
"""
Demo script to show how the manifest extracts secrets without GitHub CLI
"""

import json
from pathlib import Path

def extract_secrets_from_manifest():
    """Extract all expected secrets from manifest"""
    manifest_path = Path(__file__).parent.parent / 'config' / 'env.manifest.json'
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    expected_secrets = set()
    environments = manifest.get('environments', {})
    variables = manifest.get('variables', {})
    
    print("=" * 70)
    print(f"📋 Environment Manifest v{manifest.get('version', 'unknown')}")
    print("=" * 70)
    print()
    
    # Process explicit mappings
    print("🔑 Secrets with EXPLICIT mapping:")
    print("-" * 70)
    for category_name, category in variables.items():
        for var_name, var_config in category.items():
            if 'ci_secret_mapping' in var_config:
                print(f"\n{var_name}:")
                for env_name, secret_name in var_config['ci_secret_mapping'].items():
                    print(f"  • {env_name:20s} → {secret_name}")
                    expected_secrets.add(secret_name)
    
    # Process pattern-based secrets
    print("\n\n🎯 Secrets with PATTERN-based mapping:")
    print("-" * 70)
    for category_name, category in variables.items():
        for var_name, var_config in category.items():
            if 'ci_secret_pattern' in var_config:
                pattern = var_config['ci_secret_pattern']
                print(f"\n{var_name}: {pattern}")
                for env_name, env_config in environments.items():
                    if 'prefix' in env_config:
                        secret_name = pattern.replace('{PREFIX}', env_config['prefix'])
                        print(f"  • {env_name:20s} → {secret_name}")
                        expected_secrets.add(secret_name)
    
    # Process computed values
    print("\n\n💡 Values from ENVIRONMENT config:")
    print("-" * 70)
    for category_name, category in variables.items():
        for var_name, var_config in category.items():
            if 'value_source' in var_config and var_config['value_source'] == 'environment_config':
                print(f"\n{var_name}:")
                for env_name, env_config in environments.items():
                    if 'django_settings' in env_config:
                        print(f"  • {env_name:20s} → {env_config['django_settings']}")
    
    # Summary
    print("\n\n" + "=" * 70)
    print(f"📊 Summary: {len(expected_secrets)} unique secrets expected in GitHub")
    print("=" * 70)
    print("\nExpected secrets:")
    for secret in sorted(expected_secrets):
        print(f"  • {secret}")
    
    print("\n\n💡 To audit against GitHub:")
    print("   python config/manage_env.py audit")
    print()

if __name__ == '__main__':
    extract_secrets_from_manifest()
