from pymonkey import q, i

import yaml
from agent_service.xmppclient import XMPPClient
from agent_service.scriptexecutor import ScriptExecutor

class Agent:

    def __init__(self, agentguid, xmppServer, password, agentcontrollerguid, hostname, subscribedCallback=None):
        self.agentguid = agentguid
        self.agentcontrollerguid = agentcontrollerguid
        self.subscribedCallback = subscribedCallback

        self.xmppclient = XMPPClient(agentguid, xmppServer, password, hostname)
        self.xmppclient.setMessageReceivedCallback(self._message_received)
        self.xmppclient.setPresenceReceivedCallback(self._presence_received)

        if subscribedCallback <> None:
            def _sendSubscribe():
                self.xmppclient.sendPresence(to=self.agentcontrollerguid, type='subscribe')
                self.xmppclient.setConnectedCallback(None)

            self.xmppclient.setConnectedCallback(_sendSubscribe)

        self.xmppclient.start()

        self.scriptexecutor = ScriptExecutor()
        self.scriptexecutor.setScriptDoneCallback(self._script_done)
        self.scriptexecutor.setScriptDiedCallback(self._script_died)

    def keep_alive(self):
        self.xmppclient.keep_alive()

    def _message_received(self, fromm, type, id, message):
        if fromm == self.agentcontrollerguid:
            if type == 'start':
                self._executeScript(fromm, id, message)
            elif type == 'stop':
                self._stopScript(fromm, id)
            elif type == 'kill':
                self._killScript(fromm, id)
            else:
                q.logger.log("[AGENT] Agent '" + self.agentguid + "' received message with unknown type: '" + type + "' from the agent controller.", 4)
        else:
            q.logger.log("[AGENT] Agent '" + self.agentguid + "' received message from agent '" + fromm + "', nothing done: not the agent controller.", 5)

    def _presence_received(self, fromm, type):
        if fromm == self.agentcontrollerguid:
            if type == 'subscribe':
                q.logger.log("[AGENT] Agent '" + self.agentguid + "': agent controller asked for subscription, sending subscribed.", 5)
                self.xmppclient.sendPresence(to=self.agentcontrollerguid, type='subscribed')
            elif type == 'subscribed':
                q.logger.log("[AGENT] Agent '" + self.agentguid + "': agent controller sent subscribed.", 5)
            elif type == 'available':
                if self.subscribedCallback:
                    self.subscribedCallback()
                    self.subscribedCallback = None
        else:
            q.logger.log("[AGENT] Agent '" + self.agentguid + "' received presence from agent '" + fromm + "', nothing done: not the agentcontroller.", 5)

    def _script_done(self, fromm, jobguid, params):
        self.xmppclient.sendMessage(fromm, 'agent_done', jobguid, yaml.dump(params))

    def _script_died(self, fromm, jobguid, errorcode, erroroutput):
        self.xmppclient.sendMessage(fromm, 'agent_error', jobguid, yaml.dump({'errorcode':errorcode, 'erroroutput':erroroutput}))

    def log(self, pid, level, log_message):
        job = self.scriptexecutor.getJob(pid)
        if job == None:
            q.logger.log("[AGENT] Agent '" + self.agentguid + "' lost log info because no job was found for this pid " + str(pid), 4)
        else:
            (agentcontrollerguid, jobguid) = job
            self.xmppclient.sendMessage(agentcontrollerguid, 'agent_log', jobguid, yaml.dump({'level':level, 'message':log_message}))

    def listRunningProcesses(self):
        return map(lambda x: x.pid, self.scriptexecutor._processManager.listRunningProcesses())

    def _executeScript(self, fromm, jobguid, message):
        q.logger.log("[AGENT] Agent '" + self.agentguid + "' received script from '" + fromm + "' for job '" + jobguid + "'", 5)

        try:
            messageobject = yaml.load(message)
        except yaml.parser.ParserError:
            q.logger.log("[AGENT] Agent '" + self.agentguid + "' failed to parse the message from '" + fromm + "' for job '" + jobguid + "'", 3)
        else:
            self.scriptexecutor.execute(fromm, jobguid, messageobject["params"], messageobject["script"])

    def _stopScript(self, fromm, jobguid):
        q.logger.log("[AGENT] Agent '" + self.agentguid + "' received stop from '" + fromm + "' for job '" + jobguid + "'", 5)
        self.scriptexecutor.stop(fromm, jobguid)

    def _killScript(self, fromm, jobguid):
        q.logger.log("[AGENT] Agent '" + self.agentguid + "' received kill from '" + fromm + "' for job '" + jobguid + "'", 5)
        self.scriptexecutor.kill(fromm, jobguid)
