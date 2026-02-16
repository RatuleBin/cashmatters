from .base import *
import dj_database_url

# Local development settings - connect to Neon PostgreSQL
# DATABASES = {
#     'default': dj_database_url.config(
#         default='postgresql://neondb_owner:npg_qn6kMRwD7uJO@'
#                 'ep-silent-pond-ahfva9tj-pooler.c-3.us-east-1.aws.neon.tech/'
#                 'neondb?sslmode=require&channel_binding=require'
#     ),
#
# }
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Override any production settings for local development
DEBUG = True
SECRET_KEY = "y6eR_h82UNx40JEYo9e211ah5usQHYkqsYB9Wf_cS27ePkCpEUAzIUimeMhC4SPnSJY"

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
