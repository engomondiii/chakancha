"""
Settings module initialization
Automatically loads the correct settings based on environment
"""

import os

# Detect environment
# On Vercel, DJANGO_SETTINGS_MODULE will be set
# Locally, DJANGO_ENV determines which settings to use

# Check if we're explicitly told which settings to use
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '')

if 'production' in settings_module:
    # Vercel or production environment
    from .production import *
elif 'development' in settings_module:
    # Explicit development
    from .development import *
else:
    # Default based on DJANGO_ENV
    env = os.environ.get('DJANGO_ENV', 'development')
    
    if env == 'production':
        from .production import *
    else:
        from .development import *