from django.apps import AppConfig

import logging

logger = logging.getLogger()

class GoodsmediaConfig(AppConfig):
    name = 'goodsmedia'

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals
        logger.info('goods media app ready')
