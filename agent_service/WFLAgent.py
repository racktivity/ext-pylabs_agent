from pymonkey import q, i
from agent_service.agent import Agent
import base64

class AgentConfig:
    def __init__(self):
        try:
            config = i.config.agent.getConfig('main')
        except KeyError:
            q.logger.log("Agent failed to find the 'main' configuration: not starting.", 1)
            raise

        self.interval = int(config['cron_interval']) if 'cron_interval' in config else 10
        self.agentguid = config['agentguid']
        self.xmppserver = config['xmppserver']
        self.password = config['password']
        self.hostname = config['hostname'] if 'hostname' in config else None
        self.agentcontrollerguid = config['agentcontrollerguid']
        self.subscribed = config['subscribed'] if 'subscribed' in config else None
        self.cronEnabled = config['enable_cron'] == 'True' if 'enable_cron' in config else True

    def updateConfig(self):
        config = dict()
        config['cron_interval'] = self.interval
        config['agentguid'] = self.agentguid
        config['xmppserver'] = self.xmppserver
        config['password'] = self.password
        config['hostname'] = self.hostname
        config['agentcontrollerguid'] = self.agentcontrollerguid
        config['subscribed'] = self.subscribed
        config['enable_cron'] = self.cronEnabled
        i.config.agent.configure('main', config)


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
    def log(self, pid, level, log_message):
        log_message = base64.decodestring(log_message)
        self.__agent.log(pid, level, log_message)
        return True

    @q.manage.applicationserver.expose
    def listRunningProcesses(self):
        return self.__agent.listRunningProcesses()

    @q.manage.applicationserver.expose
    def get_agent_id(self):
        return self.__agent.agentguid
