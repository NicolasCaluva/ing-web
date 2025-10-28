import os
from pathlib import Path

from .settings import *

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/data/db.sqlite3',
    }
}

if 'django.contrib.postgres' in INSTALLED_APPS:
    INSTALLED_APPS.remove('django.contrib.postgres')

STATIC_ROOT = '/data/staticfiles'

MEDIA_ROOT = '/data/media'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': '/data/whoosh_index',
    },
}

print("Usando configuración Docker con SQLite")
print(f"Base de datos: /data/db.sqlite3")
print(f"Archivos estáticos: {STATIC_ROOT}")
print(f"Archivos media: {MEDIA_ROOT}")

