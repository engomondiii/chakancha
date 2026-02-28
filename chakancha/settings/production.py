"""
Production settings for Chakancha Backend
"""

from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.vercel.app',
    'chakancha-ai-chatbot-backend.vercel.app',
]

# Add environment variable for custom domain if you have one
if os.environ.get('ALLOWED_HOST'):
    ALLOWED_HOSTS.append(os.environ.get('ALLOWED_HOST'))

# CORS settings for production
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'https://chakancha-ai-chatbot-frontend.vercel.app',
]

# Add environment variable for custom frontend domain
if os.environ.get('FRONTEND_URL'):
    CORS_ALLOWED_ORIGINS.append(os.environ.get('FRONTEND_URL'))

CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'https://chakancha-ai-chatbot-frontend.vercel.app',
    'https://*.vercel.app',
]

# Database
# Use SQLite for Vercel (serverless doesn't persist files, but works for testing)
# For production, use PostgreSQL (Supabase)
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to SQLite (not recommended for production)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/db.sqlite3',  # Vercel /tmp directory
        }
    }

# Security settings
SECURE_SSL_REDIRECT = False  # Vercel handles SSL
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
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
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'chatbot': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Static files (already configured in base.py with WhiteNoise)
# No additional config needed

print("✅ Using PRODUCTION settings")