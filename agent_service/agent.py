from pymonkey import q, i

import yaml
import time
from agent_service.xmppclient import XMPPClient
from agent_service.scriptexecutor import ScriptExecutor
from scheduler import Scheduler
from XMPPRobot import *
from logtarget import XMPPLogTarget
from collections import defaultdict



class Agent:
    
    
    def __init__(self):
        self.scheduler = Scheduler()

    def initialize(self, agentname, xmppServers, password, agentcontrollername, domain, subscribedCallback=None):
        self.agentname = agentname        
        self._startTime = time.time()
        self.agentJID = "%s@%s"%(agentname, domain)
        self.agentcontrollername = agentcontrollername
        self.subscribedCallback = subscribedCallback
        
        self.xmppclients = dict()
        if subscribedCallback <> None:
            def _sendSubscribe(server):
                self.xmppclients[server].sendPresence(to=self.agentcontrollername, type='subscribe')
                self.xmppclients[server].setConnectedCallback(None)
                
        for xmppServer in xmppServers:
            self.xmppclients[xmppServer] = XMPPClient(agentname, xmppServer, password, domain)
            self.xmppclients[xmppServer].setMessageReceivedCallback(self._message_received)
            self.xmppclients[xmppServer].setPresenceReceivedCallback(self._presence_received)
            if subscribedCallback <> None: 
                self.xmppclients[xmppServer].setConnectedCallback(_sendSubscribe)




        self.scriptexecutor = ScriptExecutor()
        
        self._factory = TaskletEngineFactory()
        self._commandExecuter = CommandExecuter(self._factory, self.xmppclients, self.scriptexecutor)
        self._xmppLogTarget = XMPPLogTarget(self)
        q.logger.logTargetAdd(self._xmppLogTarget)
        
        for xmppclient in self.xmppclients.values():
            xmppclient.start()
        


    def _message_received(self, fromm, type, id, message, xmppServer):
        q.logger.log("[AGENT] Agent '" + self.agentname + "' received message with type: '" + type + "' from the agent controller.", 6)
        self._commandExecuter.execute(fromm, message, id, xmppServer)

    def _presence_received(self, fromm, type, xmppServer):
        if fromm == self.agentcontrollername:
            if type == 'subscribe':
                q.logger.log("[AGENT] Agent '" + self.agentname + "': agent controller asked for subscription, sending subscribed.", 5)
                self.xmppclients[xmppServer].sendPresence(to=self.agentcontrollername, type='subscribed')
            elif type == 'subscribed':
                q.logger.log("[AGENT] Agent '" + self.agentname + "': agent controller sent subscribed.", 5)
            elif type == 'available':
                if self.subscribedCallback:
                    self.subscribedCallback(xmppServer)
                    self.subscribedCallback = None
        else:
            q.logger.log("[AGENT] Agent '" + self.agentname + "' received presence from agent '" + fromm + "', nothing done: not the agentcontroller.", 5)

#    def _script_done(self, fromm, jobguid, params):
#        self.xmppclient.sendMessage(fromm, 'agent_done', jobguid, yaml.dump(params))
#
#    def _script_died(self, fromm, jobguid, errorcode, erroroutput):
#        self.xmppclient.sendMessage(fromm, 'agent_error', jobguid, yaml.dump({'errorcode':errorcode, 'erroroutput':erroroutput}))

    def log(self, pid=0, tasknr=0, level=5, message=''):        
        tasknr = tasknr or (self.scriptexecutor.getJob(pid)[1] if self.scriptexecutor.getJob(pid) else 0)
        
        if not tasknr:
            q.logger.log("[AGENT] Agent [" + self.agentname + "] lost log info. invalid arguments tasknr: %s pid: %s"%(tasknr, pid), 4)
        else:
            #self.xmppclient.sendMessage(agentcontrollerguid, 'agent_log', jobguid, yaml.dump({'level':level, 'message':message}))            
            if tasknr in self._commandExecuter.getTaskNrs():
                self.xmppclients[self._commandExecuter.getXmppServerFromTasknr(tasknr)].sendMessage(self._commandExecuter.getJIDFromTasknr(tasknr), 'chat', self._commandExecuter.generateXMPPMessageID(), '@%s|%s'%(tasknr,message))

    def listRunningProcesses(self):
        return str(map(lambda x: x.pid, self.scriptexecutor._processManager.listRunningProcesses()))

#    def _executeScript(self, fromm, jobguid, message):
#        q.logger.log("[AGENT] Agent '" + self.agentname + "' received script from '" + fromm + "' for job '" + jobguid + "'", 5)
#
#        try:
#            messageobject = yaml.load(message)
#        except yaml.parser.ParserError:
#            q.logger.log("[AGENT] Agent '" + self.agentname + "' failed to parse the message from '" + fromm + "' for job '" + jobguid + "'", 3)
#        else:
#            self.scriptexecutor.execute(fromm, jobguid, messageobject["params"], messageobject["script"])
#
#    def _stopScript(self, fromm, jobguid):
#        q.logger.log("[AGENT] Agent '" + self.agentname + "' received stop from '" + fromm + "' for job '" + jobguid + "'", 5)
#        self.scriptexecutor.stop(fromm, jobguid)
#
#    def _killScript(self, fromm, jobguid):
#        q.logger.log("[AGENT] Agent '" + self.agentname + "' received kill from '" + fromm + "' for job '" + jobguid + "'", 5)
#        self.scriptexecutor.kill(fromm, jobguid)
        
       
#    def sendLog(self, tasknr, message):        
#        if tasknr in self._commandExecuter.tasknrToJID:
#            self.xmppclient.sendMessage(self._commandExecuter.tasknrToJID[tasknr], 'chat', self._commandExecuter.generateXMPPMessageID(), '@%s|%s'%(tasknr,message))
            
    def getUpTime(self):
        return time.time() - self._startTime      

