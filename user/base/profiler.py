import cProfile
import io
import os
import time
from django.conf import settings
import tempfile

import pstats

try:
    profile_base_dir = settings.PROFILE_LOG_BASE
except:
    profile_base_dir = tempfile.gettempdir()


def profile(tag, log_file='profile.prof'):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof',
    where the time stamp is in UTC. This makes it easy to run and compare
    multiple trials.
    """
    if not os.path.exists(profile_base_dir):
        os.mkdir(profile_base_dir)

    if not os.path.isabs(log_file):
        log_file = os.path.join(profile_base_dir, log_file)

    def _outer(func):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            if not settings.DEBUG:
                ret = func(*args, **kwargs)
            else:
                (base, ext) = os.path.splitext(log_file)
                base = base + "-" + time.strftime("%Y%m%d", time.gmtime())
                final_log_file = base + ext
                prof = cProfile.Profile()
                prof.enable()
                try:
                    ret = prof.runcall(func, *args, **kwargs)
                    s = io.StringIO()
                    ps = pstats.Stats(prof, stream=s).sort_stats('cumtime')
                    ps.print_stats()
                    with open(final_log_file, 'a+') as f:
                        f.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + '_' + tag + ' *************************')
                        f.write(s.getvalue())
                finally:
                    prof.disable()
            return ret
        return _inner
    return _outer



