import os

from .base import *  # noqa: F403

DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'crm_test'),
        'USER': os.getenv('POSTGRES_USER', 'crm'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'crm'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
