"""
Django settings for dondeestudiar project.
"""
import logging
from pathlib import Path
import os
import dj_database_url

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Seguridad
# =========================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

# =========================
# Aplicaciones
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.staticfiles',

    # Haystack
    'haystack',

    # Apps propias
    'app.base',
    'app.comments',
    'app.users',
    'app.reports',
    'app.schools',
    'app.panel',

    # Cloudinary
    'cloudinary_storage',
    'cloudinary',
]

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': BASE_DIR / 'whoosh_index',
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise para estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.base.middleware.ExceptionLoggingMiddleware',  # Captura y loguea TODAS las excepciones
]

ROOT_URLCONF = 'dondeestudiar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dondeestudiar.wsgi.application'

# =========================
# Password validation
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================
# Internacionalización
# =========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =========================
# Archivos estáticos y media
# =========================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# =========================
# Primary key default
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# =========================
# Configuración para Render
# =========================
if 'RENDER' in os.environ:
    print("⚡ USING RENDER.COM SETTINGS!")
    DEBUG = True
    ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME')]
    DATABASES = {'default': dj_database_url.config(conn_max_age=600)}
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get("CLOUD_NAME"),
        'API_KEY': os.environ.get("API_KEY"),
        'API_SECRET': os.environ.get("API_SECRET"),
    }
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
    # LOG_LEVEL se determinará de forma centralizada más abajo
else:
    GOOGLE_MAPS_API_KEY = ""
    # LOG_LEVEL se determinará de forma centralizada más abajo

# Determinar LOG_LEVEL centralmente: por defecto INFO en DEBUG, WARNING en producción
LOG_LEVEL = os.environ.get('DJANGO_LOG_LEVEL', 'INFO' if DEBUG else 'WARNING').upper()

if not DEBUG:
    STORAGES = {
        # Archivos subidos (media) -> Cloudinary
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        # Archivos estáticos -> WhiteNoise
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# =========================
# Configuración para envío de correos con Gmail
# =========================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "noreply.dondeestudiar@gmail.com"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# Asegurar que la contraseña del host de email pueda venir de la variable de entorno
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': LOG_LEVEL,
            'formatter': 'custom',
        },
    },
    'formatters': {
        'custom': {
            # Incluir nivel y nombre del logger para identificar origen y severidad
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
    },
    'loggers': {
        'app.base': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'app.comments': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        # Registrar logs de Django para mayor visibilidad
        'django': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
    # Logger raíz
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
}

try:
    from .local_settings import *

    print("⚡ Usando local_settings.py")
except ImportError:
    print("⚡ No se encontró local_settings.py")
    pass
