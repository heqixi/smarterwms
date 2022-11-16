from django.apps import AppConfig

import logging

logger = logging.getLogger()


class ProductMediaConfig(AppConfig):
    name = 'productmedia'

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals
        logger.info('product media app ready')
