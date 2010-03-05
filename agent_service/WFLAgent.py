from pymonkey import q, i
from agent_service.agent import Agent
import base64
import binascii

class AgentConfig:
    def __init__(self):
        """
        Initialize configuration
        """
        add = False
        if 'main' in i.config.agent.list() and not 'agentguid' in i.config.agent.getConfig('main'):
            config = i.config.agent.getConfig('main')
        else:
            add = True
            con = i.config.cloudApiConnection.find('main')
            mac = self._getMacaddress(con)

            config = con.machine.registerAgent(mac)['result']

            config['hostname']=config.get('hostname', config['xmppserver'])
            config['xmppserver']=con._server
            q.logger.log('registerAgent UPDATE %r'%config)

        self._setConfig(config)
        if add:
            i.config.agent.add('main', self._getConfig())

    def _setConfig(self, config):
        """
        Set properties based on config dict
        @param config: config dict
        """
        self.interval = int(config['cron_interval']) if 'cron_interval' in config else 10
        self.agentguid = config['agentguid']
        self.xmppserver = config['xmppserver']
        self.password = config['password']
        self.hostname = config.get('hostname',self.xmppserver)
        self.agentcontrollerguid = config['agentcontrollerguid']
        self.subscribed = config['subscribed'] if 'subscribed' in config else None
        self.cronEnabled = config['enable_cron'] == 'True' if 'enable_cron' in config else False

    def _getMacaddress(self, con):
        """
        Retrieve the macaddress of the machine to register the agent
        @param con: cloudAPI connection
        """
        import sys
        if sys.platform=='win32':
            return '00:00:00:00:00:00'
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
        return config

    def updateConfig(self):
        """
        Update agent config file
        """
        i.config.agent.configure('main', self._getConfig())

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

    @q.manage.applicationserver.cronjob(60)
    def keep_alive(self):
        self.__agent.keep_alive()

    @q.manage.applicationserver.expose
    def log(self, pid, level, log_message):
        try:
            log_message = base64.decodestring(log_message)
        except binascii.Error:
            log_message = log_message
        self.__agent.log(pid, level, log_message)
        return True

    @q.manage.applicationserver.expose
    def listRunningProcesses(self):
        return self.__agent.listRunningProcesses()

    @q.manage.applicationserver.expose
    def get_agent_id(self):
        """
        Retrieve the guid of the agent
        """
        return self.__agent.agentguid
