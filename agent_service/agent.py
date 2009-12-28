from pymonkey import q, i

import yaml
from agent_service.xmppclient import XMPPClient
from agent_service.scriptexecutor import ScriptExecutor
from scheduler import Scheduler
from XMPPRobot import *
from logtarget import XMPPLogTarget
from collections import defaultdict





class Agent:

    def __init__(self, agentguid, xmppServer, password, agentcontrollerguid, hostname, subscribedCallback=None):
        self.agentguid = agentguid
        self.agentJID = "%s@%s"%(agentguid, xmppServer)
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
        
        self._tasknr = 0        
        #self._jobIDToTasknr = dict() this is for the production output
        self._jobIDToTasknr = defaultdict(lambda:1)  # this is a temporary, because pidgen generate new id each time 
        self._factory = TaskletEngineFactory()
        self._commandExecuter = CommandExecuter(self._factory, self.xmppclient, self.scriptexecutor)
        self._xmppLogTarget = XMPPLogTarget(self)
        q.logger.logTargetAdd(self._xmppLogTarget)
        
        self.scheduler = Scheduler()
        


    def _message_received(self, fromm, type, id, message):
        q.logger.log("[AGENT] Agent '" + self.agentguid + "' received message with type: '" + type + "' from the agent controller.", 6)
        if type == 'start':
            self._executeScript(fromm, id, message)
        elif type == 'stop':
            self._stopScript(fromm, id)
        elif type == 'kill':
            self._killScript(fromm, id)
        else:
            self._commandExecuter.execute(fromm, message, id)

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

    def log(self, pid=0, tasknr=0, level=5, message=''):
        q.logger.log('DEBUG: agent.log(pid=%s, tasknr=%s, level=%s, message=%s, jobMapping:%s )'%(pid, tasknr, level, message, self.listRunningProcesses()))
        tasknr = tasknr or (self.scriptexecutor.getJob(pid)[1] if self.scriptexecutor.getJob(pid) else 0)
        
        if not tasknr:
            q.logger.log("[AGENT] Agent [" + self.agentguid + "] lost log info. invalid arguments tasknr: %s pid: %s"%(tasknr, pid), 4)
        else:
            #self.xmppclient.sendMessage(agentcontrollerguid, 'agent_log', jobguid, yaml.dump({'level':level, 'message':message}))
            q.logger.log('DEBUG: log(tasknr:%s, message:%s, level:%s)'%(tasknr, message, level))
            if tasknr in self._commandExecuter.tasknrToJID:
                self.xmppclient.sendMessage(self._commandExecuter.tasknrToJID[tasknr], 'chat', self._commandExecuter.generateXMPPMessageID(), '@%s|%s'%(tasknr,message))

    def listRunningProcesses(self):
        return str(map(lambda x: x.pid, self.scriptexecutor._processManager.listRunningProcesses()))

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
        
       
    def sendLog(self, tasknr, message):
        q.logger.log('DEBUG: sendLog(tasknr:%s, message:%s)'%(tasknr, message))
        if tasknr in self._commandExecuter.tasknrToJID:
            self.xmppclient.sendMessage(self._commandExecuter.tasknrToJID[tasknr], 'chat', self._commandExecuter.generateXMPPMessageID(), '@%s|%s'%(tasknr,message))  
    
        
