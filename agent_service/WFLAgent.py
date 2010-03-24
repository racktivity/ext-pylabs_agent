from pymonkey import q, i
from agent_service.agent import Agent
import base64
import binascii

class AgentConfig:
    def __init__(self):
        """
        Initialize configuration
        """

        if 'main' in i.config.agent.list():
            config = i.config.agent.getConfig('main')
            i.config.agent.remove('main')
        else:
            config = dict()

        if not 'agentguid' in config:
            con = i.config.cloudApiConnection.find('main')
            mac = self._getMacaddress(con)

            config.update(con.machine.registerAgent(mac)['result'])

            config['hostname']=config.get('hostname', config['xmppserver'])
            config['xmppserver']=con._server
            q.logger.log('registerAgent UPDATE %r'%config)

        self._setConfig(config)
        i.config.agent.add('main', self._getConfig())

    def _setConfig(self, config):
        """
        Set properties based on config dict
        @param config: config dict
        """
        self.interval = int(config['cron_interval']) if 'cron_interval' in config else 10
        self.agentguid = config.get('agentguid', None)
        self.xmppserver = config.get('xmppserver', '127.0.0.1')
        self.password = config.get('password', None)
        self.hostname = config.get('hostname',self.xmppserver)
        self.agentcontrollerguid = config.get('agentcontrollerguid', None)
        self.subscribed = config.get('subscribed', None)
        self.cronEnabled = config['enable_cron'] == 'True' if 'enable_cron' in config else False
        self.passwd = config.get('passwd', 'qbase_agent')
        self.login = config.get('login', 'qbase_agent')
        self.domain = config.get('domain', 'qbase_agent')

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
        config['login'] = self.login
        config['passwd'] = self.passwd
        config['domain'] = self.domain
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

    def __del__(self):
        self.__agent.disconnect()
