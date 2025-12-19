from .base import *

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "your-production-secret-key-change-this-immediately"

# ALLOWED_HOSTS - Update with your actual domain/IP
ALLOWED_HOSTS = ["your-domain.com", "www.your-domain.com", "your-server-ip"]

# Database configuration for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cashmatters_db',
        'USER': 'cashmatters_user',
        'PASSWORD': 'your_secure_db_password_here',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',  # Enable SSL for production
        }
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
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/django/apps/cashmatters/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
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
