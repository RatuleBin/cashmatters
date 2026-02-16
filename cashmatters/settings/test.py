from .base import *

# Test settings
SECRET_KEY = "test-secret-key-not-for-production"

# Allow test domains
# ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']
ALLOWED_HOSTS = ['*']

# Use SQLite for tests (much faster and more reliable in CI)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': ':memory:',
#     }
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Use in-memory email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable debug for tests
DEBUG = True

# Test-specific settings
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Media files for tests
MEDIA_ROOT = '/tmp/test_media'
STATIC_ROOT = '/tmp/test_static'
