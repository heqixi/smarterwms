from django.contrib import admin
from timer.executor import AsyncSchedulerExecutor
from . models import ListModel

admin.site.register(ListModel)

# AsyncSchedulerExecutor.get_instance().register(task=SyncBrandTask())
