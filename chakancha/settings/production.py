"""
Production settings for Chakancha Backend
Optimized for Vercel serverless deployment
"""

from .base import *
import os
import sys

# Disable console output for API key validation
sys.argv = ['vercel']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.vercel.app',
    'chakancha-ai-chatbot-backend.vercel.app',
]

# Add custom domain if provided
custom_host = os.environ.get('ALLOWED_HOST')
if custom_host:
    ALLOWED_HOSTS.append(custom_host)

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://chakancha-ai-chatbot-frontend.vercel.app',
]

# Add custom frontend URL if provided
frontend_url = os.environ.get('FRONTEND_URL')
if frontend_url:
    CORS_ALLOWED_ORIGINS.append(frontend_url)

CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'https://chakancha-ai-chatbot-frontend.vercel.app',
    'https://*.vercel.app',
]

# Database Configuration
# Vercel serverless doesn't support persistent SQLite
# Use PostgreSQL (Supabase) for production or temp SQLite for testing

if os.environ.get('DATABASE_URL'):
    # Use PostgreSQL if DATABASE_URL is provided
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to SQLite in /tmp (not persistent, resets on each deployment)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',
        }
    }

# Security Settings
SECURE_SSL_REDIRECT = False  # Vercel handles SSL termination
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'chatbot': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'agents': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Static files are handled by WhiteNoise (configured in base.py)
# No additional configuration needed

print("✅ Using PRODUCTION settings for Vercel")