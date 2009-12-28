import unittest
import base64
import xmlrpclib
from pymonkey import q,i

class SchedulerClient(object):
    def __init__(self):
        self._ip = q.config.getConfig('applicationserver')['main']['xmlrpc_ip']
        portAsString = q.config.getConfig('applicationserver')['main']['xmlrpc_port']
        self._port = int(portAsString) if portAsString else 0
        self._proxy = xmlrpclib.ServerProxy('http://%(ip)s:%(port)s/'%{'ip':self._ip, 'port':self._port}, allow_none=True)
        
    def start(self, groupName=None):        
        self._proxy.agent_service.start(groupName)        
    
    def stop(self, groupName=None):
        self._proxy.agent_service.stop(groupName)
        
    def getStatus(self, groupName=None):
        return self._proxy.agent_service.getStatus(groupName)

    def getUpTime(self):
        return self._proxy.agent_service.getUpTime()
    
    def getParams(self, groupName=None):
        return self._proxy.agent_service.getParams(groupName)
