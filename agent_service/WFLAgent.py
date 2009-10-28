from pymonkey import q, i
from agent_service.agent import Agent
import base64

class AgentConfig:
    def __init__(self):
        try:
            self.configure = i.config.agent.getConfig('main')
        except KeyError:
            q.logger.log("Agent failed to find the 'main' configuration: not starting.", 1)
            raise

        self.interval = int(self.configure['cron_interval'])
        self.agentguid = self.configure['agentguid']
        self.xmppserver = self.configure['xmppserver']
        self.password = self.configure['password']
        self.agentcontrollerguid = self.configure['agentcontrollerguid']
        self.subscribe = self.configure['subscribed'] if 'subscribed' in self.configure else None
        self.cronEnabled = self.configure['enable_cron'] == 'True' if 'enable_cron' in self.configure else True

config = AgentConfig()

class WFLAgent:
    def __init__(self, path=None):
        if not path:
            path = q.system.fs.joinPaths(q.dirs.appDir, 'applicationserver', 'services', 'agent_service', 'tasklets')

        if not q.system.fs.exists(path):q.system.fs.createDir(path)
        self.taskletEngine = q.getTaskletEngine(path)

        if config.subscribe:
            self.__agent = Agent(config.agentguid, config.xmppserver, config.password, config.agentcontrollerguid)

        else:
            def _onSubscribed():
                config.configure['subscribed'] = True
                i.config.agent.configure('main', config.configure)

            self.__agent = Agent(config.agentguid, config.xmppserver, config.password, config.agentcontrollerguid, _onSubscribed)


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
