"""
WSGI config for chakancha project.
Configured for Vercel serverless deployment.
"""

import os
from django.core.wsgi import get_wsgi_application

# Force production settings on Vercel
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chakancha.settings.production')

application = get_wsgi_application()

# Vercel requires this
app = application