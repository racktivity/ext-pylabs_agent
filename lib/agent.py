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

'''
PyLabs agent module
'''
import signal
import traceback
from agentacl import AgentACL
from robot import Robot, TaskManager
from xmppclient import XMPPClient, XMPPTaskNumberMessage, XMPPResultMessage, XMPPLogMessage
from pymonkey.inifile import IniFile
from pymonkey import q


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
        self._servers = dict() 
        self._isEnabled = dict()
        self._tasknumberToClient= dict()
        
        if not 'agent' in q.config.list():
            raise RuntimeError('Agent config file %s does not exist')
        
        sections = q.config.getConfig('agent') 
        for sectionInfo in sections.values(): 
            if 'agentname' in sectionInfo:
                jid = "%s@%s"%(sectionInfo.get('agentname'), sectionInfo.get('domain'))
                self.accounts[jid] = XMPPClient(jid, sectionInfo.get('password'))
                self.acl[jid] = AgentACL(sectionInfo.get('agentname'), sectionInfo.get('domain'))
                self._servers[jid] = sectionInfo.get('server')
                # register the required events
                self.accounts[jid].setCommandReceivedCallback(self._onCommandReceived)
                self.accounts[jid].setLogReceivedCallback(self._onLogReceived)
                self.accounts[jid].setErrorReceivedCallback(self._onErrorReceived)
                self.accounts[jid].setResultReceivedCallback(self._onResultReceived)
                self.accounts[jid].setMessageReceivedCallback(self._onMessageReceived)
                enabled = sectionInfo.get('enabled')
                self._isEnabled[jid] = True if enabled == '1' or enabled == 'True' else False                
                
        self.robot = Robot()
        self.robot.setOnPrintReceivedCallback(self._onPrintReceived)
        self.robot.setOnExceptionReceivedCallback(self._onExceptionReceived)
        
        self.taskManager = TaskManager(self.robot)
        self.robot.setTaskCompletedCallback(self._onTaskCompleted)
        
        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT, self._stop)
        
    def _stop(self, signum, frames):
        self.stop()        

    def connectAccount(self, jid):
        """
        Connects the account with the JID specified
        
        @param jid:                  JID of the account to connect 
        @type jid:                   string

        @return:                     True is case account connected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        if not jid in self.accounts:
            q.logger.log('Account %s does not exist'% jid)
            return
        
        if not self._isEnabled[jid]:
            q.logger.log('Account %s is not enabled'% jid)
            return
        
        self.accounts[jid].connect(self._servers[jid])
        self._status = q.enumerators.AppStatusType.RUNNING
    
    def disconnectAccount(self, jid):
        """
        Disconnects the account with the JID specified
        
        @param jid:                  JID of the account to disconnect 
        @type jid:                   string

        @return:                     True is case account disconnected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        
        if not jid in self.accounts:
            q.logger.log('Account %s does not exist'% jid)
            return
        
        self.accounts[jid].disconnect()

    def connectAllAccounts(self):
        """
        Connects all accounts
        
        @return:                     True is case all accounts connected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        for jid in self.accounts.keys():
            if self._isEnabled[jid]:
                self.accounts[jid].connect(self._servers[jid])
    
    def disconnectAllAccounts(self):
        """
        Disconnects all accounts
        
        @return:                     True is case all accounts disconnected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        
        for jid in self.accounts.keys():
            if self._isEnabled[jid]:
                self.accounts[jid].disconnect()

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
        
        if not xmppmessage.sender in self.accounts:
            q.logger.log('Account %s does not exist'% xmppmessage.sender)
            return
        
        self.accounts[xmppmessage.sender].sendMessage(xmppmessage)
    
    
    def start(self):
        """
        Starts the agent and connects all enabled accounts automatically
       
        @return:                     True is case all accounts connected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        
        self.connectAllAccounts()
        self._status = q.enumerators.AppStatusType.RUNNING
        q.logger.log('[Agent] starting the robot taskmanager....')
        self.taskManager.start()

    def stop(self):
        """
        Stops the agent
        
        @return:                     True is case all accounts disconnected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        
        self.disconnectAllAccounts()
        self._status = q.enumerators.AppStatusType.HALTED

    def getStatus(self):
        """
        Gets the status of the agent
        
        @return:                     Returns q.enumerators.AppStatusType
        @rtype:                      q.enumerators.AppStatusType

        @raise e:                    In case an error occurred, exception is raised
        """
        return self._status

    
    def _onCommandReceived(self, xmppCommandMessage):
        """
        # Check for which account message is
        # Ask robot which tasklets match
        # Check ACL for corresponding account if sender is authorized to execute command on this agent
        # Instruct robot to execute command

        REMARK!
        ## Kill and stop are exceptions, the should call killTask or stopTask on robot
        """
        q.logger.log('Command Message is received: %s'% xmppCommandMessage.format())
        
        jid = xmppCommandMessage.sender
        if not xmppCommandMessage.receiver  in self.acl:
            q.logger.log('Account %s has no ACLs'% xmppCommandMessage.receiver)
            return
            
        tags = [xmppCommandMessage.command]        
        if xmppCommandMessage.subcommand:
            tags.append(xmppCommandMessage.subcommand)
                        
        try:
            taskletsPaths = self.robot.findCommands(tuple(tags))
            if not taskletsPaths:
                q.logger.log('No Tasklets found for command:%s ,subcommand:%s'%(xmppCommandMessage.command, xmppCommandMessage.subcommand))
            
            for taskletPath in taskletsPaths:
                if not self.acl[xmppCommandMessage.receiver].isAuthorized(jid, taskletPath):
                    q.logger.log(' [%s] is not authorized to execute this tasklet:%s'%(jid, taskletPath))
                    return
            
            tasknumber = self.robot.getNextTaskNumber()
            
            if xmppCommandMessage.command.lower() == 'killtask':
                taskToBeKilled = int(xmppCommandMessage.params['params'][0])
                if self.robot.killTask(taskToBeKilled):
                    self.sendMessage(XMPPResultMessage(xmppCommandMessage.receiver, xmppCommandMessage.sender, xmppCommandMessage.resource, xmppCommandMessage.messageid, tasknumber, 0, 'Task %s is killed successfully '%taskToBeKilled))
                else:
                    self.sendMessage(XMPPResultMessage(xmppCommandMessage.receiver, xmppCommandMessage.sender, xmppCommandMessage.resource, xmppCommandMessage.messageid, tasknumber, 1, 'Task %s could not be killed'%taskToBeKilled))   
            elif xmppCommandMessage.command.lower() == 'stoptask':
                taskToBeStooped = int(xmppCommandMessage.params['params'][0])
                if self.robot.stopTask(taskToBeStooped):                
                    self.sendMessage(XMPPResultMessage(xmppCommandMessage.receiver, xmppCommandMessage.sender, xmppCommandMessage.resource, xmppCommandMessage.messageid, tasknumber, 0, 'Task %s stopped successfully '%taskToBeStooped))
                else:
                    self.sendMessage(XMPPResultMessage(xmppCommandMessage.receiver, xmppCommandMessage.sender, xmppCommandMessage.resource, xmppCommandMessage.messageid, tasknumber, 1, 'Task %s could not be stopped'%taskToBeStooped))
            else:                
                self._tasknumberToClient[tasknumber] = (xmppCommandMessage.receiver, xmppCommandMessage.sender, xmppCommandMessage.resource, xmppCommandMessage.messageid)
                self.robot.execute(tags, xmppCommandMessage.params, tasknumber)                
                self.sendMessage(XMPPTaskNumberMessage(sender = xmppCommandMessage.receiver, receiver = xmppCommandMessage.sender, resource = xmppCommandMessage.resource, messageid = xmppCommandMessage.messageid, tasknumber = tasknumber))
        except Exception, ex:
            q.logger.log('[Agent] Exception Occurred while trying to execute the command %s'%ex)
            

    def _onLogReceived(self, xmppLogMessage):
        """
        """
        q.logger.log('Log Message is received: %s'% xmppLogMessage.format())        
        

    def _onErrorReceived(self, xmppErrorMessage):
        """       
        """
        q.logger.log('Error Message is received: %s'% xmppErrorMessage.format())

    def _onResultReceived(self, xmppResultMessage):
        """
        """
        q.logger.log('Result Message is received: %s'% xmppResultMessage.format())

    def _onMessageReceived(self, xmppMessage):
        """
        """
        q.logger.log('XMPP Message is received: %s'% xmppMessage.format())
        
    
    def _onTaskCompleted(self, tasknumber, returncode, returnvalue):
        """
        callback method that will be called when an robot task completed
        
        @param tasknumber: the tasknumber of the task that finished
        @param returncode: the result returncode
        @param returnvalue: the value of the message
        """
        q.logger.log('Task %s completed, result message will be constructed..'%tasknumber)
        sender, receiver, resource, messageid = self._tasknumberToClient[tasknumber]
        del self._tasknumberToClient[tasknumber]
        self.sendMessage(XMPPResultMessage(sender, receiver, resource, messageid, tasknumber, returncode, returnvalue))
        
    def _onPrintReceived(self, tasknumber, string):
        if not string.strip():
            return
        q.logger.log('Task %s prints: %s'%(tasknumber,string))
        sender, receiver, resource, messageid = self._tasknumberToClient[tasknumber]
        q.logger.log('DEBUG: OnPrintReceived -> sender:%s, receiver:%s, messageid:%s'%(sender, receiver, messageid))
        self.sendMessage(XMPPLogMessage(sender, receiver, resource, messageid, tasknumber, string))
        
    def _onExceptionReceived(self, tasknumber, type_, value, tb):
        q.logger.log('DEBUG: tasknumber:%s, typeOfException:%s, value:%s, tb:%s'%(tasknumber, type_, value, tb))
        sender, receiver, resource, messageid = self._tasknumberToClient[tasknumber]
        q.logger.log('DEBUG: OnExceptionReceived -> sender:%s, receiver:%s, messageid:%s'%(sender, receiver, messageid))
        self.sendMessage(XMPPLogMessage(sender, receiver, resource, messageid, tasknumber, "Exception: %s"%traceback.format_exception(type_, value, tb)))
        
