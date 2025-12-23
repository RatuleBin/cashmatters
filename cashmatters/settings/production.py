from .base import *
import os

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-key-change-in-production')

# ALLOWED_HOSTS - Update with your actual domain/IP
ALLOWED_HOSTS = ["72.62.147.13", "localhost", "127.0.0.1"]

# Database configuration for production - Railway PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'railway'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD',
                          'eYMpmsmByJvGdqVNLfwhHZkjEnAdUVTU'),
        'HOST': os.getenv('POSTGRES_HOST', 'crossover.proxy.rlwy.net'),
        'PORT': os.getenv('POSTGRES_PORT', '39397'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}


# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email configuration (update with your SMTP settings)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP provider
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-email-password'

# Static and media files
STATIC_URL = '/static/'
STATIC_ROOT = '/home/django/apps/cashmatters/staticfiles/'

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/django/apps/cashmatters/media/'

# Wagtail settings for production
WAGTAIL_SITE_NAME = 'CashMatters'

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ManifestStaticFilesStorage is recommended in production
STORAGES["staticfiles"]["BACKEND"] = \
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

try:
    from .local import *
except ImportError:
    pass
