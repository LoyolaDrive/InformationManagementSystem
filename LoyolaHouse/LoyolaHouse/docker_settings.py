"""
Django settings for LoyolaHouse project when running in Docker.
This file extends the base settings.py with Docker-specific configurations.
"""

import os
from .settings import *

# Database configuration from environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME', 'LoyolaDB'),
        'USER': os.environ.get('DATABASE_USER', 'loyola_user'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'loyola_password'),
        'HOST': os.environ.get('DATABASE_HOST', 'db'),
        'PORT': os.environ.get('DATABASE_PORT', '3306'),
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES'
        }
    }
}

# Update allowed hosts for Docker
ALLOWED_HOSTS = ['*']

# Static and media files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
