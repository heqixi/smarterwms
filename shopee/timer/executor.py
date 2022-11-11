import asyncio
import logging
import sys
import threading
from abc import abstractmethod

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger()


class Task(object):

    @abstractmethod
    def job_id(self):
        pass

    @abstractmethod
    def trigger_args(self):
        """
        参数参考：https://blog.csdn.net/RoninYang/article/details/121131548
        """
        pass

    @abstractmethod
    def do_exec(self):
        pass


class SchedulerExecutor(object):

    @abstractmethod
    def register(self, task: Task):
        pass

    @abstractmethod
    def remove(self, job_id):
        pass

    @abstractmethod
    def stop(self, job_id):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass


class AsyncSchedulerExecutor(SchedulerExecutor):
    """
    异步定时任务
    """
    executor = None
    timez = 'Asia/Shanghai'
    __create_key = object()
    lock = threading.RLock()

    def __init__(self, create_key):
        assert (create_key == AsyncSchedulerExecutor.__create_key), \
            "SchedulerExecutor objects must be created using SchedulerExecutor.get_instance"
        self.scheduler = AsyncIOScheduler(timezone=self.timez)

    @classmethod
    def get_instance(cls):
        if cls.executor is None:
            cls.lock.acquire()
            if cls.executor is None:
                cls.executor = cls(AsyncSchedulerExecutor.__create_key)
            cls.lock.release()
            return cls.executor
        return cls.executor

    def register(self, task: Task):
        if task is None:
            raise ValueError('Task can not be None')
        logger.info('background executor register task %s', task.job_id())
        self.scheduler.add_job(id=task.job_id(), func=task.do_exec, **task.trigger_args())
        return self

    def remove(self, job_id):
        print('Remove job ', job_id)
        self.scheduler.remove_job(job_id)

    def stop(self, job_id):
        if job_id is None:
            raise ValueError('Missing job_id')
        self.scheduler.remove_job(job_id=job_id)
        return self

    def __start(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.scheduler.start()
        loop.run_forever()

    def start(self):
        print('sys args ', sys.argv)
        if len(self.scheduler.get_jobs()) > 0 and sys.argv[1] not in ['makemigrations', 'migrate']:
            threading.Thread(target=self.__start, args=()).start()
            print('Asyncio scheduler started')
        else:
            print('Asyncio scheduler not started')

    def shutdown(self):
        print('Task scheduler shutdown')
        self.scheduler.shutdown()


class BlockSchedulerExecutor(SchedulerExecutor):
    """
    阻塞定时任务
    """
    executor = None
    timez = 'Asia/Shanghai'
    __create_key = object()
    lock = threading.RLock()

    def __init__(self, create_key):
        assert (create_key == BlockSchedulerExecutor.__create_key), \
            "SchedulerExecutor objects must be created using SchedulerExecutor.get_instance"
        self.scheduler = BackgroundScheduler(timezone=self.timez)

    @classmethod
    def get_instance(cls):
        if cls.executor is None:
            cls.lock.acquire()
            if cls.executor is None:
                cls.executor = cls(BlockSchedulerExecutor.__create_key)
            cls.lock.release()
            return cls.executor
        return cls.executor

    def register(self, task: Task):
        if task is None:
            raise ValueError('Task can not be None')
        self.scheduler.add_job(id=task.job_id(), func=task.do_exec, **task.trigger_args())
        return self

    def remove(self, job_id):
        self.scheduler.remove_job(job_id)

    def stop(self, job_id):
        if job_id is None:
            raise ValueError('Missing job_id')
        self.scheduler.remove_job(job_id=job_id)
        return self

    def start(self):
        if len(self.scheduler.get_jobs()) > 0:
            self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()
