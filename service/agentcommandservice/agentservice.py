#INCUBAID BSD version 2.0 
#Copyright (c) 2010 Incubaid BVBA
#
#All rights reserved. 
# 
#Redistribution and use in source and binary forms, with or 
#without modification, are permitted provided that the following 
#conditions are met: 
# 
#* Redistributions of source code must retain the above copyright 
#notice, this list of conditions and the following disclaimer. 
#
#* Redistributions in binary form must reproduce the above copyright 
#notice, this list of conditions and the following disclaimer in    the documentation and/or other materials provided with the   distribution. 
#* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
# 
#THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from pymonkey import q, i

from agent_service.xmppclient import XMPPClient, XMPPResultMessage, XMPPCommandMessage
from agent_service.taskcallbackmapper import TaskCallbackMapper

import time
import re

class AgentService:

    def __init__(self):        
        
        #load configuration from the config file
        configuration = q.config.getConfig('agent_service')
        
        if not 'main' in configuration:
            raise RuntimeError('main section is not found in the agent_service configuration file')
         
        self.xmppclient = XMPPClient('%s@%s'%(configuration['main']['agentname'], configuration['main']['domain']), configuration['main']['password'])
        self.xmppclient.connect(configuration['main']['server'])
        self.timeout = int(configuration['main']['timeout'])
        
        self.taskmapper = TaskCallbackMapper(self.xmppclient)
        self.finished = {}
        self.messagesReceived = {} 
        
    def _messagesReceived(self, id, xmppMessages):
        q.logger.log('message is received %s'% xmppMessages,5)
        self.messagesReceived[id] = xmppMessages
        self.finished[id] = True
    
    @q.manage.applicationserver.expose    
    def sendCommand(self, toJID, command, subcommand=None, params=None, resource=''):
        '''
        this method used to send commands to agent and return the result synchronously
        
        @param toJID: JID of agent to which the command is sent
        @type string:
        
        @param command: command to be sent, e.g portforward
        @type string:
        
        @param subcommand: subcommand, e.g open
        @type string
        
        @param params: dictionary contains two keys 'options' and 'params' , each value is list of strings , e.g params = {'params':['ls'], 'options':['-id 2123']}
        @type dict
        
        @return: true if the command is sent and executed successfully, otherwise   
        @type boolean: 
         
        '''
        idOption = filter(lambda opt: opt.startswith('-id '), params['options'])
        id = None# if no id is specified, no callback is registered
        if idOption:
            id = idOption[0][4:]
            self.taskmapper.registerTaskCallback(id, self._messagesReceived)

        xmppCommandMessage = XMPPCommandMessage(self.xmppclient.userJID, toJID, resource, id, command, subcommand, params)                
        generatedID = self.xmppclient.sendMessage(xmppCommandMessage)
        if not id:
            id = generatedID
            self.taskmapper.registerTaskCallback(id, self._messagesReceived)
                
        self.finished[id] = False
        
        timeout = self.timeout
          
        while not self.finished[id]:
            timeout -=1
            if timeout < 0: 
                return False # timeout without receiving any xmpp messages            
            time.sleep(1)
        
        #if we didn't time out above, that means a message (or more) is received, and the callback is invoked
        return self.messagesReceived[id][-1].returncode == '0'#we're sure that the last message in the list is a XmppResultMessage
    
    @q.manage.applicationserver.expose
    def openPortForward(self, toJID, serverport, localDestination, portOnDestination, loginPasswordServer, options):
        '''
        open PortForward R/L
        
        @param toJID: JID of agent to which the command is sent
        @type string: 
        
        @param serverport
        @type string:
        
        @param localDestination:
        @type string:
        
        @param portOnDestination:
        @type string:
        
        @param loginPasswordServer:
        @type string:
        
        @param options: e.g ['-R', '-id 55'] or ['-L', '-id 55'] 
        @param list:        
        
        @return: true if the command is sent and executed successfully, otherwise   
        @type boolean:        
        '''        
        args = [serverport, localDestination, portOnDestination, loginPasswordServer]
        args = map(lambda x: str(x), args) # to avoid writing any argument in type other than string
        
        params = {'params':args, 'options':options if options else []}
        return self.sendCommand(toJID, 'portforward', 'open', params)
    
    @q.manage.applicationserver.expose
    def closePortForward(self, toJID, serverport, localDestination, portOnDestination, loginPasswordServer, options):
        '''
        close PortForward R/L
        
        @param toJID: JID of agent to which the command is sent
        @type string: 
        
        @param serverport
        @type string:
        
        @param localDestination:
        @type string:
        
        @param portOnDestination:
        @type string:
        
        @param loginPasswordServer:
        @type string:
        
        @param options: e.g ['-R', '-id 55'] or ['-L', '-id 55'] 
        @param list:        
        
        @return: true if the command is sent and executed successfully, otherwise   
        @type boolean:        
        '''        
        args = [serverport, localDestination, portOnDestination, loginPasswordServer]
        args = map(lambda x: str(x), args) # to avoid writing any argument in type other than string
        
        params = {'params':args, 'options':options if options else []}
        return self.sendCommand(toJID, 'portforward', 'close', params)
    
    @q.manage.applicationserver.expose
    def getAgentsRegisteredForDomain(self, domain):
        '''
        returns a list of agents registered for this domain
        
        @param domain:    Zenith registration domain
        @type domain:     string
        '''
        
        d = self._encodeDomain(domain) 
        r = r'agent[0-9]+_%s' % d 
        
        agents = q.manage.servers.ejabberd.getRegisteredUsers('agent.sso.daas.com')
        
        return [agent for agent in agents if re.match(r, agent)]
        
        
    @q.manage.applicationserver.expose
    def getAgentsOnlineForDomain(self, domain):
        '''
        returns a list of online agents for this domain
        
        @param domain:    Zenith registration domain
        @type domain:     string
        '''
        d = self._encodeDomain(domain) 
        r = r'agent[0-9]+_%s@agent.sso.daas.com' % d 
        
        agents = q.manage.servers.ejabberd.usersConnectedList()
        
        return [agent.split('/')[0] for agent in agents if re.match(r, agent)]
        
        
    def _encodeDomain(self, domain):
        '''
        returns encoded domain representation as it is used for registering agents
        
        @param domain:    Zenith registration domain
        @type domain:     string
        '''
        
        d = domain.replace('.', '_')
        
        return d
        