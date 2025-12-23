from .base import *
import os
import dj_database_url

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "y6eR_h82UNx40JEYo9e211ah5usQHYkqsYB9Wf_cS27ePkCpEUAzIUimeMhC4SPnSJY"

# ALLOWED_HOSTS - Update with your actual domain/IP
ALLOWED_HOSTS = ["72.62.147.13", "localhost", "127.0.0.1"]

# Database configuration for production - Neon PostgreSQL
DATABASE_URL = (
    'postgresql://neondb_owner:npg_qn6kMRwD7uJO@ep-silent-pond-'
    'ahfva9tj-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require'
)
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600
    )
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
