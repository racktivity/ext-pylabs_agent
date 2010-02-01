from pymonkey import q, i
from agent_service.agent import Agent
import base64
import binascii
import xmpp


def _formatServerAddress(serverAddress, reverse = False):
    return serverAddress.replace('_', '.') if not reverse else serverAddress.replace('.', '_')

class ServerConfig:
    pass

class AgentConfig:
    def __init__(self):
        """
        Initialize configuration
        """
        
        self.serverConfigs = dict()
        xmppserverList = i.config.agent.list()
        self.registeredServers = list()
        self.cronEnabled = False
#        if 'main' in xmppserverList:
#            xmppserverList.pop(xmppserverList.index('main'))
#            agentConfig = i.config.agent.getConfig('main')
#        q.agent.register([_formatServerAddress(serverAddress) for serverAddress in xmppserverList], agentConfig['domain'], agentConfig['agentname'], agentConfig['password'])
        xmppserverList = i.config.agent.list()
        if 'main' in xmppserverList:
            agentConfig = i.config.agent.getConfig(xmppserverList.pop(xmppserverList.index('main')))
            self._setConfig(agentConfig, xmppserverList)
            self.registeredServers = [_formatServerAddress(item[0]) for item in filter(lambda config: config[1].get('registered', False), [(server, i.config.agent.getConfig(server)) for server in xmppserverList])]

    def _setConfig(self, config, xmppserverList):
        """
        Set properties based on config dict
        @param config: config dict
        """
        self.interval = int(config['cron_interval']) if 'cron_interval' in config else 10
        self.agentname = config['agentname']
        self.password = config['password']
        self.domain = config.get('domain', '') 
        self.agentcontrollername = config.get('agentcontrollername', 'agentcontroller')
        self.cronEnabled = config['enable_cron'] == 'True' if 'enable_cron' in config else False
        
        for xmppserver in xmppserverList:
            serverConfig = i.config.agent.getConfig(xmppserver)
            if not xmppserver in self.serverConfigs:
                self.serverConfigs[xmppserver] = ServerConfig()
            self.serverConfigs[xmppserver].registered = serverConfig.get('registered', False)
            self.serverConfigs[xmppserver].subscribed = serverConfig.get('subscribed', False)
        
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
        config['agentname'] = self.agentname
        config['password'] = self.password
        config['domain'] = self.domain
        config['agentcontrollername'] = self.agentcontrollername
        config['enable_cron'] = self.cronEnabled
#        config['xmppserver'] = self.xmppserver
#        config['subscribed'] = self.subscribed
#        config['registered'] = self.registered
        return config
    
    def _getServerConfig(self, server):
        config = dict()
        config['registered'] = self.serverConfigs[server].registered
        config['subscribed'] = self.serverConfigs[server].subscribed
        return config
        

    def updateConfig(self):
        """
        Update agent config file
        """
        i.config.agent.configure('main', self._getConfig())
    
    def updateServerConfig(self, server):
        """
        Update the server configuration
        
        @param server: name of the server to update
        """
        i.config.agent.configure(server, self._getServerConfig(server))
    

config = AgentConfig()

def initializationCheck(func):
    """
    Check if the agent is registered with any of the configured servers or not, if not a message is displayed
    """
    def new_func(*args, **kwargs):
        if not config.registeredServers:
            q.console.echo('Agent is not registered yet, please call q.agent.register then try again')
            return
        return func(*args, **kwargs)
    return new_func

class WFLAgent:
    def __init__(self, path=None):
        if not path:
            path = q.system.fs.joinPaths(q.dirs.appDir, 'applicationserver', 'services', 'agent_service', 'tasklets')

        if not q.system.fs.exists(path):q.system.fs.createDir(path)
        self.taskletEngine = q.getTaskletEngine(path)

        def _onSubscribed(server):
            server = _formatServerAddress(server, reverse = True)
            config.serverConfigs[server].subscribed = True
            config.updateServerConfig(server)
        self.__agent = Agent()
        
        if config.registeredServers:
            self.__agent.initialize(config.agentname, config.registeredServers, config.password, config.agentcontrollername, config.domain, _onSubscribed)
#        self.__agent = Agent(config.agentname, config.registeredServers[0], config.password, config.agentcontrollername, config.domain, _onSubscribed)
        


    if config.cronEnabled:
        @q.manage.applicationserver.cronjob(config.interval)
        @initializationCheck
        def run_scheduled(self):
            params = dict()
            params['agentguid'] = self.__agent.agentname
            self.taskletEngine.execute(params, tags = ('agent', 'schedule'))

    @q.manage.applicationserver.expose
    @initializationCheck
    def log(self, pid, level, message):
        try:
            message = base64.decodestring(message)
        except binascii.Error:
            pass             
        self.__agent.log(pid=pid, level=level, message=message)
        return True

    @q.manage.applicationserver.expose
    @initializationCheck
    def listRunningProcesses(self):
        return self.__agent.listRunningProcesses()

    @q.manage.applicationserver.expose
    @initializationCheck
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
    @initializationCheck          
    def getAgentUpTime(self):
        return self.__agent.getUpTime()
    
    