"""
Production settings - used on Vercel/Railway deployment
"""

import os
import dj_database_url
from .base import *

# Debug MUST be False in production
DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'localhost,127.0.0.1,.railway.app,.vercel.app,chakancha-ai-chatbot-backend.vercel.app'
).split(',')

# Database - PostgreSQL on Supabase
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres.ssqxcyrmtbrzfjqfkaxg:gpslab@gpslab@2025@aws-0-us-west-1.pooler.supabase.com:5432/postgres'
)

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# CORS settings for production
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'https://chakancha-ai-chatbot-frontend.vercel.app'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# Security settings
SECURE_SSL_REDIRECT = False  # Vercel handles SSL
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CSRF settings
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'https://chakancha-ai-chatbot-frontend.vercel.app,https://chakancha-ai-chatbot-backend.vercel.app'
).split(',')

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'chatbot': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print("🚀 Production settings loaded")
print(f"🌐 Allowed hosts: {ALLOWED_HOSTS}")
print(f"🔒 SSL Redirect: {SECURE_SSL_REDIRECT}")
print(f"🗄️  Database: PostgreSQL (Supabase)")