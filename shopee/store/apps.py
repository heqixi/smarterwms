from django.apps import AppConfig


class StoreConfig(AppConfig):
    name = 'store'

    def ready(self):
        from store.scheduler.storescheduler import RefreshTokenTask
        from timer.executor import AsyncSchedulerExecutor
        AsyncSchedulerExecutor.get_instance().register(RefreshTokenTask())
