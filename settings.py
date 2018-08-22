import os
from getenv import env

INSTALLED_ADDONS = [
    'django_addons',
    'django_addon',
    'django_celery_addon',
]
INSTALLED_APPS = []

import django_addons.settings
django_addons.settings.load(locals())


AUTH_USER_MODEL = 'accounts.User'


INSTALLED_APPS.extend([
    'core',
    'accounts',
    'timelapse_manager',
    'taggit',
    'rest_framework',
    'rest_framework.authtoken',
    'easy_thumbnails',
    # 'django_extensions',
])

THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': '/usr/bin/optipng -o7 {filename}',
    'gif': '/usr/bin/optipng -o7 {filename}',
    'jpeg': '/usr/bin/jpegoptim {filename}',
}


# disable multi-language support
USE_I18N = False

TIMELAPSE_STORAGE_DSN = env('TIMELAPSE_STORAGE_DSN', 'file:///data/timelapse')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissions',
    ),
    'DEFAULT_THROTTLE_RATES': {
        # 'bucket:retrieve': '2/day',
        # 'bucket:list': {
        #     'burst': '1/second',
        #     'sustained': '5/hour',
        # },
    },
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100,
}


# from aldryn_django import storage
# for storage_backend in storage.SCHEMES.values():
#     if storage_backend == DEFAULT_FILE_STORAGE:
#         THUMBNAIL_DEFAULT_STORAGE = storage_backend
#         break

LOGGING['loggers']['celery'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
}
from logging.config import dictConfig
dictConfig(LOGGING)


INSTALLED_APPS.append('graphene_django')
INSTALLED_APPS.append('django_graphiql')
GRAPHENE = {
    'MIDDLEWARE': [
        # Not sure if this is needed. It seemed to work without it too.
        'graphene_django.debug.DjangoDebugMiddleware',
    ]
}


# Django Channels
INSTALLED_APPS.insert(0, 'channels')
ASGI_APPLICATION = 'routing.application'

CHANNEL_LAYERS = {
    # FIXME: configure from env var
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis', 6379)],
        },
    },
}


# Chat tutorial
INSTALLED_APPS.append('chat')


# Progress experiment
INSTALLED_APPS.append('progress_experiment')


# Eliot and stuff
INSTALLED_APPS.append('eliot_plus.celery')
