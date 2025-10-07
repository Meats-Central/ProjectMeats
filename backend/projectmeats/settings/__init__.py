"""
Settings module initialization.
Provides easy imports for different environments.
"""

import os

# Default to development settings
environment = os.environ.get(
    "DJANGO_SETTINGS_MODULE", "projectmeats.settings.development"
)

# Import the appropriate settings
if "production" in environment:
    from .production import *
elif "staging" in environment:
    from .staging import *
else:
    from .development import *
