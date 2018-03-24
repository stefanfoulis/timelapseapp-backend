# -*- coding: utf-8 -*-
import os
from getenv import env

INSTALLED_ADDONS = [
    # <INSTALLED_ADDONS>  # Warning: text inside the INSTALLED_ADDONS tags is auto-generated. Manual changes will be overwritten.
    'django_addons',
    'django_addon',
    # 'aldryn_sso',
    'django_celery_addon',
    # </INSTALLED_ADDONS>
]
INSTALLED_APPS = []

import django_addons.settings
django_addons.settings.load(locals())


AUTH_USER_MODEL = 'accounts.User'


INSTALLED_APPS.extend([
    'accounts',
    'timelapse_manager',
    'taggit',
    'rest_framework',
    'rest_framework.authtoken',
    'easy_thumbnails',
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
