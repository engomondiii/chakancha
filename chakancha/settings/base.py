"""
Django settings for chakancha project.
Base settings - common to all environments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-CHANGE-IN-PROD-ch4k4nch4-2025-abc123xyz')

# Application definition
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'chatbot.apps.ChatbotConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS - must be before CommonMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Custom middleware for logging
    'api.middleware.RequestLoggingMiddleware',
    'api.middleware.CORSLoggingMiddleware',
]

ROOT_URLCONF = 'chakancha.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chakancha.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/minute',  # 60 requests per minute for anonymous users
    },
    'DEFAULT_AUTHENTICATION_CLASSES': [],  # No auth for now (public chatbot)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Public access
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# ═══════════════════════════════════════════════════════
# CHAKANCHA-SPECIFIC CONFIGURATION
# ═══════════════════════════════════════════════════════

# Chatbot Settings
CHATBOT_CONFIG = {
    'MAX_MESSAGE_LENGTH': 2000,
    'MAX_CONVERSATION_HISTORY': 10,  # Keep last 10 messages in memory
    'SESSION_TIMEOUT_HOURS': 24,
    'DEFAULT_LANGUAGE': 'en',
}

# ═══════════════════════════════════════════════════════
# API KEYS & EXTERNAL SERVICES (WITH FALLBACK DEFAULTS)
# ═══════════════════════════════════════════════════════

# Anthropic Claude API (Cloud Sonnet - Chakancha Chatbot)
ANTHROPIC_API_KEY = os.environ.get(
    'ANTHROPIC_API_KEY',
    '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'
)

# OpenAI API (Embeddings for RAG System)
OPENAI_API_KEY = os.environ.get(
    'OPENAI_API_KEY',
    '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'
)

# Pinecone Vector Database (RAG FAQ Storage)
PINECONE_API_KEY = os.environ.get(
    'PINECONE_API_KEY',
    'pcsk_3SHH1W_8WMkx7xRXocgrkiN2TtqFrev3z3RFgxUYDfXqrxGMwSzSygAqh5eW97pFG8pVHJ'
)
PINECONE_ENVIRONMENT = os.environ.get('PINECONE_ENVIRONMENT', 'us-east-1')
PINECONE_INDEX_NAME = os.environ.get('PINECONE_INDEX_NAME', 'chakancha-faq-en')

# Supabase (Database & Storage)
SUPABASE_URL = os.environ.get(
    'SUPABASE_URL',
    'https://ssqxcyrmtbrzfjqfkaxg.supabase.co'
)
SUPABASE_KEY = os.environ.get(
    'SUPABASE_KEY',
    'sb_publishable_Ifl4V96Kxg3tizMdKPfY4g_EZo3IBYc'
)

# DHL API (Phase 5 - Empty by default, uses mock mode)
DHL_API_KEY = os.environ.get('DHL_API_KEY', '')

# ═══════════════════════════════════════════════════════
# API KEY VALIDATION (Development Only)
# ═══════════════════════════════════════════════════════

# Verify critical API keys are set on startup
def validate_api_keys():
    """Print warnings for missing API keys in development"""
    import sys
    
    # Only check in development
    if 'runserver' in sys.argv or 'shell' in sys.argv:
        warnings = []
        
        if not ANTHROPIC_API_KEY:
            warnings.append("⚠️  ANTHROPIC_API_KEY not set")
        else:
            print("✅ Anthropic API Key: Set")
        
        if not OPENAI_API_KEY:
            warnings.append("⚠️  OPENAI_API_KEY not set")
        else:
            print("✅ OpenAI API Key: Set")
        
        if not PINECONE_API_KEY:
            warnings.append("⚠️  PINECONE_API_KEY not set")
        else:
            print("✅ Pinecone API Key: Set")
        
        if warnings:
            print("\n" + "="*60)
            for warning in warnings:
                print(warning)
            print("="*60 + "\n")

# Run validation
validate_api_keys()