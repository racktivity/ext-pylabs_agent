import unittest
import base64
import xmlrpclib
from pymonkey import q,i
from SchedulerClient import SchedulerClient

class AgentClient(object):
    def __init__(self):
        self._ip = q.config.getConfig('applicationserver')['main']['xmlrpc_ip']
        portAsString = q.config.getConfig('applicationserver')['main']['xmlrpc_port']
        self._port = int(portAsString) if portAsString else 0
        self._proxy = xmlrpclib.ServerProxy('http://%(ip)s:%(port)s/'%{'ip':self._ip, 'port':self._port}, allow_none=True)
        self.scheduler = SchedulerClient(self._proxy)
        
    def start(self):        
        serviceName = 'agent_service'
        classspec = 'agent_service.WFLAgent.WFLAgent'
        if not serviceName in i.servers.applicationserver.services.list():
            i.servers.applicationserver.services.add(serviceName, {'classspec':classspec})
            q.manage.applicationserver.restart()        
    
    def stop(self):
        i.servers.applicationserver.services.remove('agent_service')
        q.manage.applicationserver.restart()
        
    def getStatus(self,):
        return 'Running' if 'agent_service' in i.servers.applicationserver.services.list() else 'Halted'

    def getUpTime(self):
        return self._proxy.agent_service.getAgentUpTime() if 'agent_service' in i.servers.applicationserver.services.list() else 0;
    
