from .base import *

# Local development settings - override database to use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cashmatters_db',
        'USER': 'cashmatters_user',
        'PASSWORD': 'secure_password_123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Override any production settings for local development
DEBUG = True
SECRET_KEY = 'local-development-key-change-in-production'

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
