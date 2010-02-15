'''
INCUBAID BSD version 2.0 
Copyright (c) 2010 Incubaid BVBA

All rights reserved. 
 
Redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following 
conditions are met: 
 
* Redistributions of source code must retain the above copyright 
notice, this list of conditions and the following disclaimer. 

* Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in    the documentation and/or other materials provided with the   distribution. 
* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
 
THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

PyLabs agent module
'''
from agentacl import AgentACL
from robot import Robot, RobotTask
from xmppclient import XMPPClient, XMPPMessage, XMPPCommandMessage, XMPPResultMessage, XMPPLogMessage, XMPPErrorMessage, XMPPTaskNumberMessage
from pymonkey.inifile import IniFile
from pymonkey import q

class Account(object):    
    def __init__(self, agentname, domain, password, server):
        self.agentname = agentname
        self.domain = domain
        self.password = password
        self.server = server    


class Agent(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        
        '''
        
        """
        for every account in agent.cfg
            client = XMPPClient(jid, password)
            # set all callback methods
            client.setCommandReceivedCallback = self._onCommandReceived
            self.accounts[jid] = client
            self.acl[jid] = AgentACL(agentname, domain)
        self.robot = Robot()
        """
        self.accounts = dict()
        self.acl = dict()
        self.servers = dict() 
        agentConfigFile = q.system.fs.joinPaths(q.dirs.cfgDir, 'qconfig', 'agent.cfg')
        
        if not q.system.fs.isFile(agentConfigFile):
            raise RuntimeError('Agent config file %s does not exit'%agentConfigFile)
        cfgFile = IniFile(agentConfigFile)
        for section in cfgFile.getSections():            
            sectionInfo = cfgFile.getSectionAsDict(section)
            if sectionInfo.get('agentname'):
                jid = "%s@%s"%(sectionInfo.get('agentname'), sectionInfo.get('domain'))
                self.accounts[jid] = XMPPClient(jid, sectionInfo.get('password'))
                self.acl[jid] = AgentACL(sectionInfo.get('agentname'), sectionInfo.get('domain'))
                self.servers[jid] = sectionInfo.get('server')
                # register the required events
                self.accounts[jid].setCommandReceivedCallback(self._onCommandReceived)
                self.accounts[jid].setLogReceivedCallback(self._onLogReceived)
                self.accounts[jid].setErrorReceivedCallback(self._onErrorReceived)
                self.accounts[jid].setResultReceivedCallback(self._onResultReceived)
                self.accounts[jid].setMessageReceivedCallback(self._onMessageReceived)                
                
                
        self.robot = Robot()

    def connectAccount(self, jid):
        """
        Connects the account with the JID specified
        
        @param jid:                  JID of the account to connect 
        @type jid:                   string

        @return:                     True is case account connected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        if not self.accounts.has_key(jid):
            raise RuntimeError('Account %s does not exist'% jid)
        
        self.accounts[jid].connect(self.servers[jid])
    
    def disconnectAccount(self, jid):
        """
        Disconnects the account with the JID specified
        
        @param jid:                  JID of the account to disconnect 
        @type jid:                   string

        @return:                     True is case account disconnected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        
        if not self.accounts.has_key(jid):
            raise RuntimeError('Account %s does not exist'% jid)
        
        self.accounts[jid].disconnect()

    def connectAllAccounts(self):
        """
        Connects all accounts
        
        @return:                     True is case all accounts connected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        for jid in self.accounts.keys():
            self.accounts[jid].connect(self.servers[jid])
    
    def disconnectAllAccounts(self):
        """
        Disconnects all accounts
        
        @return:                     True is case all accounts disconnected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        
        for account in self.accounts.values():
            account.disconnect()

    def sendMessage(self, xmppmessage):
        """
        @param xmppmessage           XMPP message
        @type xmppmessage            XMPPMessage

        @return:                     Unique identifier for this message
        @rtype:                      string

        @raise e:                    In case an error occurred, exception is raised
        """
        
        """
        self.accounts[xmppmessage.sender].sendMessage(xmppmessage)
        """
        
        if not self.accounts.has_key(xmppmessage.sender):
            raise RuntimeError('Account %s does not exist'% xmppmessage.sender)
        
        self.accounts[xmppmessage.sender].sendMessage(xmppmessage)
    
    def _onCommandReceived(self, xmppCommandMessage):
        """
        # Check for which account message is
        # Ask robot which tasklets match
        # Check ACL for corresponding account if sender is authorized to execute command on this agent
        # Instruct robot to execute command

        REMARK!
        ## Kill and stop are exceptions, the should call killTask or stopTask on robot
        """
        
        jid = xmppCommandMessage.sender
        tags = [xmppCommandMessage.command]
        if xmppCommandMessage.subcommand:
            tags.append(xmppCommandMessage.subcommand)
                        
        tasklets = self.robot.findCommands(tags)
        if not tasklets:
            raise RuntimeError('No Tasklets found for command:% ,subcommand:%'%(xmppCommandMessage.command, xmppCommandMessage.subcommand))
        
        for tasklet in tasklets:
            if not self.acl[jid].isAuthorized(xmppCommandMessage.receiver, tasklet.path):
                raise RuntimeError(' [%s] is not authorized to execute this tasklet:%s'%( xmppCommandMessage.receiver, tasklet.path))
        
        self.robot.execute(tags, xmppCommandMessage.params)

    def _onLogReceived(self, XMPPLogMessage):
        """
        """

    def _onErrorReceived(self, XMPPErrorMessage):
        """       
        """

    def _onResultReceived(self, XMPPResultMessage):
        """
        """

    def _onMessageReceived(self, XMPPMessage):
        """
        """
