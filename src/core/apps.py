from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        # initialise eliot
        from . import logging
