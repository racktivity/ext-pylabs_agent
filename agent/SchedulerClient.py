import unittest
import base64
import xmlrpclib
from pymonkey import q,i

class SchedulerClient(object):
    def __init__(self, proxy):
        self._proxy = proxy
        
    def start(self, groupName=None):        
        self._proxy.agent_service.startScheduler(groupName)        
    
    def stop(self, groupName=None):
        self._proxy.agent_service.stopScheduler(groupName)
        
    def getStatus(self, groupName=None, includeHalted=False):
        return self._proxy.agent_service.getSchedulerStatus(groupName, includeHalted)

    def getUpTime(self):
        return self._proxy.agent_service.getSchedulerUpTime()
    
    def getParams(self, groupName=None):
        return self._proxy.agent_service.getSchedulerParams(groupName)
    
    def listGroups(self):
        return self._proxy.agent_service.listSchedulerGroups()
    
