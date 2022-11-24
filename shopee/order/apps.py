from django.apps import AppConfig


class OrderConfig(AppConfig):
    name = 'order'

    # def ready(self):
    #     # Scheduler register
    #     from order.scheduler.orderscheduler import SyncOrderTask, SyncReadyToShipOrderTask
    #     from timer.executor import AsyncSchedulerExecutor
    #     AsyncSchedulerExecutor.get_instance() \
    #         .register(task=SyncOrderTask()) \
    #         .register(task=SyncReadyToShipOrderTask())
