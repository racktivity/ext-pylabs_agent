from pymonkey import q, i
from agent_service.agent import Agent

class WFLAgent:
    
    def __init__(self):
        try:
            config = i.config.agent.getConfig('main')
        except KeyError:
            q.logger.log("Agent failed to find the 'main' configuration: not starting.", 1)
            raise
        else:
            if 'subscribed' in config:
                self.__agent = Agent(config['agentguid'], config['xmppserver'], config['password'], config['agentcontrollerguid'])
            else:
                def _onSubscribed():
                    config['subscribed'] = True
                    i.config.agent.configure('main', config)
                
                self.__agent = Agent(config['agentguid'], config['xmppserver'], config['password'], config['agentcontrollerguid'], _onSubscribed)
    
    @q.manage.applicationserver.expose
    def log(self, pid, level, log_message):
        return self.__agent.log(pid, level, log_message)
    
    @q.manage.applicationserver.expose
    def listRunningProcesses(self):
        return self.__agent.listRunnlistRunningProcesses()
