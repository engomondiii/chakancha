"""
Settings module initialization
Automatically loads the correct settings based on DJANGO_ENV
"""

import os

# Get environment from env variable, default to development
ENVIRONMENT = os.environ.get('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    from .production import *
    print("✅ Using PRODUCTION settings")
else:
    from .development import *
    print("✅ Using DEVELOPMENT settings")