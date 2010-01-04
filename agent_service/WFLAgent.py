from pymonkey import q, i
from agent_service.agent import Agent
import base64
import binascii
import xmpp


class AgentConfig:
    def __init__(self):
        """
        Initialize configuration
        """
        if 'main' in i.config.agent.list():
            config = i.config.agent.getConfig('main')
            self._setConfig(config)
            if not 'registered' in i.config.agent.getConfig('main'):
                self.registerAgent(config)


    def _setConfig(self, config):
        """
        Set properties based on config dict
        @param config: config dict
        """
        self.interval = int(config['cron_interval']) if 'cron_interval' in config else 10
        self.agentguid = config['agentguid']
        self.xmppserver = config['xmppserver']
        self.password = config['password']
        self.hostname = config['hostname'] if 'hostname' in config else self.xmppserver 
        self.agentcontrollerguid = config['agentcontrollerguid']
        self.subscribed = config['subscribed'] if 'subscribed' in config else None
        self.cronEnabled = config['enable_cron'] == 'True' if 'enable_cron' in config else False
        self.registered = config['registered'] if 'registered' in config else None

    def _getMacaddress(self, con):
        """
        Retrieve the macaddress of the machine to register the agent
        @param con: cloudAPI connection
        """
        ipaddress = q.system.net.getReachableIpAddress(con._server, con._port)
        return q.system.net.getMacAddressForIp(ipaddress).upper() or '00:00:00:00:00:00'

    def _getConfig(self):
        """
        Construct config dict from properties
        """
        config = dict()
        config['cron_interval'] = self.interval
        config['agentguid'] = self.agentguid
        config['xmppserver'] = self.xmppserver
        config['password'] = self.password
        config['hostname'] = self.hostname
        config['agentcontrollerguid'] = self.agentcontrollerguid
        config['subscribed'] = self.subscribed
        config['enable_cron'] = self.cronEnabled
        config['registered'] = self.registered
        return config

    def updateConfig(self):
        """
        Update agent config file
        """
        i.config.agent.configure('main', self._getConfig())
        
    
    def registerAgent(self, config):
        client = xmpp.Client(config['xmppserver'])
        if not client.connect():
            raise RuntimeError('Failed to connect to xmppserver %s'%config['xmppserver'])
        
        def _registered(conn, event):
            if event.getType() == 'result' and int(event.getID()) == 2:
                config['registered'] = True
                self.updateConfig()
            elif event.getType() != 'result':
                raise RuntimeError('Failed to register agent with config %s with xmppserver %s. Reason %s'%(config, config['xmppserver'], event.getBody()))
        try:    
            client.RegisterHandler('iq', _registered)
            iq = xmpp.Iq('get', xmpp.NS_REGISTER)
            client.send(iq)
            q.logger.log('[AGENT] calling client.Process')
            client.Process(1)
            q.logger.log('[AGENT] after calling calling client.Process')
            iq = xmpp.Iq('set', xmpp.NS_REGISTER)
            iq.T.query.NT.username = config['agentguid']
            iq.T.query.NT.password = config['password']
            client.send(iq)
            client.Process(1)
        except Exception, ex:
            raise RuntimeError('Failed to register agent with config %s with xmppserver %s. Reason: %s'%(config, config['xmppserver'], ex))
        q.logger.log('[AGENT]:agent with guid %s registered successfully with xmppserver %s'%(config['agentguid'], config['xmppserver']))


config = AgentConfig()

class WFLAgent:
    def __init__(self, path=None):
        if not path:
            path = q.system.fs.joinPaths(q.dirs.appDir, 'applicationserver', 'services', 'agent_service', 'tasklets')

        if not q.system.fs.exists(path):q.system.fs.createDir(path)
        self.taskletEngine = q.getTaskletEngine(path)

        def _onSubscribed():
            config.subscribed = True
            config.updateConfig()

        self.__agent = Agent(config.agentguid, config.xmppserver, config.password, config.agentcontrollerguid, config.hostname, _onSubscribed)
        


    if config.cronEnabled:
        @q.manage.applicationserver.cronjob(config.interval)
        def run_scheduled(self):
            params = dict()
            params['agentguid'] = self.__agent.agentguid
            self.taskletEngine.execute(params, tags = ('agent', 'schedule'))

    @q.manage.applicationserver.expose
    def log(self, pid, level, message):
        try:
            message = base64.decodestring(message)
        except binascii.Error:
            pass             
        self.__agent.log(pid=pid, level=level, message=message)
        return True

    @q.manage.applicationserver.expose
    def listRunningProcesses(self):
        return self.__agent.listRunningProcesses()

    @q.manage.applicationserver.expose
    def get_agent_id(self):
        """
        Retrieve the guid of the agent
        """
        return self.__agent.agentJID
    
    @q.manage.applicationserver.expose
    def startScheduler(self, groupName=None):
        self.__agent.scheduler.start(groupName)        
    
    @q.manage.applicationserver.expose
    def stopScheduler(self, groupName=None):
        self.__agent.scheduler.stop(groupName)
        
    @q.manage.applicationserver.expose
    def getSchedulerStatus(self, groupName=None, includeHalted=False):
        return self.__agent.scheduler.getStatus(groupName, includeHalted)

    @q.manage.applicationserver.expose
    def listSchedulerGroups(self):
        return self.__agent.scheduler.listGroups()

    @q.manage.applicationserver.expose            
    def getSchedulerUpTime(self):
        return self.__agent.scheduler.getUpTime()
    
    @q.manage.applicationserver.expose
    def getSchedulerParams(self, groupName):
        return self.__agent.scheduler.getParams(groupName)
    
    @q.manage.applicationserver.expose    
    def setSchedulerParams(self, groupName, params):
        self.__agent.scheduler.setParams(groupName, params)
        
    @q.manage.applicationserver.expose            
    def getAgentUpTime(self):
        return self.__agent.getUpTime()
    
    