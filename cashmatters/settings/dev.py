from .base import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "y6eR_h82UNx40JEYo9e211ah5usQHYkqsYB9Wf_cS27ePkCpEUAzIUimeMhC4SPnSJY"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["72.62.147.13", "localhost", "127.0.0.1"]
# ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Media files configuration for development
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

try:
    from .local import *
except ImportError:
    pass
