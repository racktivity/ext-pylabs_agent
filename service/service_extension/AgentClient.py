import unittest
import base64
import xmlrpclib
from pymonkey import q,i
from pymonkey.inifile import IniFile

import xmpp

DEFAULXMPPTPORT = 5222

class AgentClient(object):
    def __init__(self):
        self._ip = q.config.getConfig('applicationserver')['main']['xmlrpc_ip']
        portAsString = q.config.getConfig('applicationserver')['main']['xmlrpc_port']
        self._port = int(portAsString) if portAsString else 0
        self._proxy = xmlrpclib.ServerProxy('http://%(ip)s:%(port)s/'%{'ip':self._ip, 'port':self._port}, allow_none=True)
    
              
    def sendCommand(self, toJID, command, subcommand=None, params=None, resource=''):
        return self._proxy.agent_service.sendCommand(toJID, command, subcommand, params, resource)
    
    def openPortForward(self, toJID, serverport, localDestination, portOnDestination, loginPasswordServer, options):        
        return self._proxy.agent_service.openPortForward(toJID, serverport, localDestination, portOnDestination, loginPasswordServer, options)

