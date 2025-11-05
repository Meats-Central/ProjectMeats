#!/usr/bin/env python3
"""
Script to remove temporary debug logging for staging.meatscentral.com.
Run this after verifying that staging is working correctly.

Usage:
    python3 remove_debug_logging.py
"""

import re
import sys
from pathlib import Path


def remove_debug_logging():
    """Remove all [STAGING DEBUG] logging from middleware."""
    middleware_file = Path("backend/apps/tenants/middleware.py")
    backup_file = middleware_file.with_suffix('.py.backup')
    
    if not middleware_file.exists():
        print(f"Error: Middleware file not found at {middleware_file}")
        return False
    
    # Read original content
    with open(middleware_file, 'r') as f:
        original_content = f.read()
    
    # Create backup
    print(f"Creating backup at {backup_file}...")
    with open(backup_file, 'w') as f:
        f.write(original_content)
    
    # Process line by line to remove debug blocks
    lines = original_content.split('\n')
    cleaned_lines = []
    skip_block = False
    block_indent = None
    
    for line in lines:
        # Check for start of staging debug block
        # Note: This is string matching in source code, not URL validation
        if 'is_staging' in line and '=' in line and 'staging.meatscentral.com' in line:
            skip_block = True
            block_indent = len(line) - len(line.lstrip())
            continue
        
        # Check for if is_staging: conditions
        if 'if is_staging:' in line:
            skip_block = True
            block_indent = len(line) - len(line.lstrip())
            continue
        
        # If we're in a skip block
        if skip_block:
            current_indent = len(line) - len(line.lstrip())
            
            # Empty lines or lines more indented than block start - skip
            if line.strip() == '' or current_indent > block_indent:
                continue
            else:
                # We've dedented - stop skipping
                skip_block = False
                block_indent = None
        
        # Keep this line
        cleaned_lines.append(line)
    
    # Join back together
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Additional cleanup: remove any remaining [STAGING DEBUG] references
    cleaned_content = re.sub(r'\s*logger\.(info|error)\([^)]*\[STAGING DEBUG\][^)]*\)\s*', '', cleaned_content)
    
    # Write cleaned content
    with open(middleware_file, 'w') as f:
        f.write(cleaned_content)
    
    print(f"✓ Debug logging removed from {middleware_file}")
    print(f"✓ Backup saved to {backup_file}")
    print()
    print("Next steps:")
    print(f"1. Review the changes: git diff {middleware_file}")
    print("2. Test the application to ensure it still works")
    print(f"3. Commit the changes: git add {middleware_file} && git commit -m 'Remove temporary staging debug logging'")
    print(f"4. Remove backup if satisfied: rm {backup_file}")
    
    return True


if __name__ == '__main__':
    try:
        success = remove_debug_logging()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

