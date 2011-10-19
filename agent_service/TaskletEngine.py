from pymonkey.taskletengine.TaskletEngine4 import TaskletEngine4
from cloud_api_client.Exceptions import CloudApiException
from pymonkey.Shell import *
import os
import os.path
import sys
import imp
import random
import inspect
import operator
import time
import stat
import functools
import logging
import pymonkey

try:
    import threading
except ImportError:
    threading = None

MATCH_FAILED = object()


class TaskletEngine(TaskletEngine4):
    def execute(self, params, author="*", name="*", tags=None, priority=-1, wrapper=None):
        '''Execute all matching tasklets and continue in case of errors

        @param params: Params to pass to the tasklet function,is a dict
        @type params: dict
        @param wrapper: Optional function decorator which can be used to wrap
                        tasklet main() functions
        @type wrapper: callable

        @see: TaskletsEngine.find
        '''
        realized = set()

        matches = self.find(author, name, tags, priority)

        for tasklet in matches:
            if tasklet.realizes and tasklet.realizes in realized:
                pymonkey.q.logger.log('%s already realized, ' \
                                      'skipping tasklet %s' % \
                                      (tasklet.realizes, tasklet.name), 6)
                continue
            try:
                ret = tasklet.executeIfMatches(params, tags or tuple(), wrapper)
            except Exception,e:
                pymonkey.q.logger.log('Tasklet %s raised exception' %tasklet.name)
                for traceback in sys.exc_info():
                    pymonkey.q.logger.log('Tasklet error: %s' %traceback)
                continue

            if ret is not MATCH_FAILED and tasklet.realizes:
                pymonkey.q.logger.log('%s realized by %s' % (tasklet.realizes,
                                                    tasklet.name), 6)
                realized.add(tasklet.realizes)

            if ret is self.STOP:
                break


