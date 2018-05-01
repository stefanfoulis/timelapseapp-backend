# -*- coding: utf-8 -*-

import django.apps


class AppConfig(django.apps.AppConfig):

    name = 'eliot_plus.celery'
    verbose_name = 'Eliot Plus Celery'

    def ready(self):
        # pylint: disable=unused-import
        # noinspection PyUnresolvedReferences
        from . import signals
