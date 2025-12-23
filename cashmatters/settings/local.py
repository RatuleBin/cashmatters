from .base import *

# Local development settings - connect to Railway PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'eYMpmsmByJvGdqVNLfwhHZkjEnAdUVTU',
        'HOST': 'crossover.proxy.rlwy.net',
        'PORT': '39397',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Override any production settings for local development
DEBUG = True
SECRET_KEY = 'local-development-key-change-in-production'

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
