import unittest
import base64
import xmlrpclib
from pymonkey import q,i
from pymonkey.inifile import IniFile
from SchedulerClient import SchedulerClient

import xmpp

DEFAULXMPPTPORT = 5222

class AgentClient(object):
    def __init__(self):
        self._ip = q.config.getConfig('applicationserver')['main']['xmlrpc_ip']
        portAsString = q.config.getConfig('applicationserver')['main']['xmlrpc_port']
        self._port = int(portAsString) if portAsString else 0
        self._proxy = xmlrpclib.ServerProxy('http://%(ip)s:%(port)s/'%{'ip':self._ip, 'port':self._port}, allow_none=True)
        self.scheduler = SchedulerClient(self._proxy)
        self.cfgFile = IniFile(self._getDefaultConfigFile(), create = not q.system.fs.exists(self._getDefaultConfigFile()))
        
    
    def _getDefaultConfigFile(self):
        return q.system.fs.joinPaths(q.dirs.cfgDir, 'qconfig', 'agent.cfg')
    
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
    
    #@todo: move the functionality of sinnig up with a xmppserver to the xmppclient, and here just write the configuration file
    def _registerAgent(self, xmppserver, domain, agentname, agentpassword):
        client = xmpp.Client(domain, debug = [])
        if not client.connect((xmppserver, DEFAULXMPPTPORT)):
            raise RuntimeError('Failed to connect to xmppserver %s'%xmppserver)
        
        def _registered(conn, event):
            if event.getType() == 'result' and 'instructions' not in map(lambda node: node.getName(), event.getQueryPayload()):
                self.cfgFile.setParam(self._formatServerAddress(xmppserver), 'registered', True)
            elif event.getType() == 'error' and 'conflict' in map(lambda node: node.getName(), event.getQueryPayload()):
                q.console.echo('Agent %s@%s already registered on server %s'%(agentname, domain, xmppserver))
        try:    
            client.RegisterHandler('iq', _registered)
            iq = xmpp.Iq('get', xmpp.NS_REGISTER)
            client.send(iq)
            client.Process(1)
            iq = xmpp.Iq('set', xmpp.NS_REGISTER)
            iq.T.query.NT.username = agentname
            iq.T.query.NT.password = agentpassword
            client.send(iq)
            client.Process(1)
        except Exception, ex:
            raise RuntimeError('Failed to register agent %s@%s with xmppserver %s. Reason: %s'%(agentname, domain, agentpassword, ex))
        q.logger.log('[AGENT]:agent %s@%s registered successfully with xmppserver %s'%(agentname, domain, agentpassword))
    
    
    
    def register(self, xmppserverlist, domain, agentname, agentpassword):
        """
        Register agent with a list of xmppserver list on a specific domain, if the agent is already registered a message printed and 
        try to register with the other servers, after registeration the info is written into a config file
        
        @param xmppserverlist: list of xmppserver names that will need to register with
        @param domain: the domain in the xmppserver in which the agent will register
        @param agentname: name of the agent 
        @param agentpassword: password of the agent     
        """
        
        #@todo: check if the main info changed from the existing one(if any)
        agentConfig = {'agentname': agentname, 'password': agentpassword, 'domain': domain, 'agentcontrollername': 'agentcontroller', 'enable_cron': True, 'cron_interval': 10}
        if not self.cfgFile.checkSection('main'):
            self.cfgFile.addSection('main')
            
        #this will overwrite the old config of main section
        for key, value in agentConfig.items():
            self.cfgFile.setParam('main', key, value)
             
        for xmppserver in xmppserverlist:
            formatted_xmppserver = self._formatServerAddress(xmppserver)
            if not formatted_xmppserver in self.cfgFile.getSections():
                serverSection = {'registered': False, 'subscribed': False}
#                    i.config.agentv4.configure(xmppserver, config)
                self.cfgFile.addSection(formatted_xmppserver)
                for key, value in serverSection.items():
                    self.cfgFile.addParam(formatted_xmppserver, key, value)
                self._registerAgent(xmppserver, domain, agentname, agentpassword)
            elif self.cfgFile.getSectionAsDict(formatted_xmppserver).get('registered', False):
                self._registerAgent(xmppserver, domain, agentname, agentpassword)
            else:
                q.logger.log('[AGENT] agent %s@%s is already registered on server %s'%(agentname, domain, xmppserver), 5)
        q.manage.applicationserver.restart()
        
        
    def _formatServerAddress(self, serverAddress):
        return serverAddress.replace('.', '_')
        