#!/usr/bin/env python3
"""
Setup.py for ProjectMeats3 - pip compatible version.

This file provides pip compatibility for Digital Ocean App Platform
and other deployment platforms that expect a standard setup.py.

For development environment setup, use: python setup_env.py
"""

import sys
import os

# Always try setuptools first for any standard command
try:
    from setuptools import setup
    
    # If we have a standard setuptools command or are being called by pip, use setuptools
    if (len(sys.argv) > 1 and sys.argv[1] in [
        'egg_info', 'bdist_wheel', 'sdist', 'build', 'install', 'develop',
        'build_py', 'build_ext', 'build_clib', 'build_scripts', 'dist_info',
        'editable_wheel'
    ]) or len(sys.argv) == 1:
        # All configuration is in pyproject.toml
        setup()
        sys.exit(0)
        
except ImportError:
    pass

# If we get here, it's likely a direct user call asking for environment setup
print("For development environment setup, this script has been moved.")
print("Please use: python setup_env.py")
print()
print("Available options:")
print("  python setup_env.py           # Full setup (backend + frontend)")
print("  python setup_env.py --backend # Backend only")
print("  python setup_env.py --frontend# Frontend only")  
print("  python setup_env.py --help    # Show help")
sys.exit(1)