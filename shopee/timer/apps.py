from django.apps import AppConfig
from timer.executor import AsyncSchedulerExecutor
import logging

logger = logging.getLogger()


class TimerConfig(AppConfig):
    name = 'timer'

    def ready(self):
        AsyncSchedulerExecutor.get_instance().start()

