from pymonkey import q, i

from agent_service.xmppclient import XMPPClient, XMPPResultMessage, XMPPCommandMessage
from agent_service.taskcallbackmapper import TaskCallbackMapper

import time

class AgentService:
    def __init__(self):        
        
        #load configuration from the config file
        configuration = q.config.getConfig('agent_service')
        
        if not 'main' in configuration:
            raise RuntimeError('main section is not found in the agent_service configuration file')
         
        self.xmppclient = XMPPClient('%s@%s'%(configuration['main']['agentname'], configuration['main']['domain']), configuration['main']['password'])
        self.xmppclient.connect(configuration['main']['server'])
        
        self.taskmapper = TaskCallbackMapper(self.xmppclient)
        self.finished = {}
        self.messagesReceived = {} 
        
    def _messagesReceived(self, id, xmppMessages):
        q.logger.log('message is received %s'% xmppMessages,5)
        self.messagesReceived[id] = xmppMessages
        self.finished[id] = True
    
    @q.manage.applicationserver.expose    
    def sendCommand(self, toJID, command, subcommand=None, params=None, resource=''):
        idOption = filter(lambda opt: opt.startswith('-id '), params['options'])
        id = None# if no id is specified, no callback is registered
        if idOption:
            id = idOption[0][4:]
            self.taskmapper.registerTaskCallback(id, self._messagesReceived)

        xmppCommandMessage = XMPPCommandMessage(self.xmppclient.userJID, toJID, resource, id, command, subcommand, params)                
        id = self.xmppclient.sendMessage(xmppCommandMessage)
        if not idOption:
            self.taskmapper.registerTaskCallback(id, self._messagesReceived)
                
        self.finished[id] = False
        
        timeout = 20 # for timeout
          
        while not self.finished[id]:
            timeout -=1
            if timeout < 0: 
                return False # timeout without receiving any xmpp messages            
            time.sleep(0.5)
        
        #if we didn't time out above, that means a message (or more) is received, and the callback is invoked
        return self.messagesReceived[id][-1].returncode == '0'#we're sure that the last message in the list is a XmppResultMessage
    
    @q.manage.applicationserver.expose
    def openPortForward(self, toJID, serverport, localDestination, portOnDestination, loginPasswordServer, options):
        args = [serverport, localDestination, portOnDestination, loginPasswordServer]
        params = {'params':args, 'options':options if options else []}
        return self.sendCommand(toJID, 'portforward', 'open', params)