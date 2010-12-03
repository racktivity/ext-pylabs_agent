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
import signal, time
import traceback
from agentacl import AgentACL
from robot import Robot
from xmppclient import XMPPClient, XMPPTaskNumberMessage, XMPPResultMessage, XMPPLogMessage, XMPPCommandMessage

from pymonkey.inifile import IniFile
from pymonkey import q

from xmpplogtarget import XMPPLogTarget
from taskcallbackmapper import TaskCallbackMapper

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

        self.reloadConfig()

        self.robot = Robot()
        self.robot.setOnPrintReceivedCallback(self._onPrintReceived)
        self.robot.setOnExceptionReceivedCallback(self._onExceptionReceived)

        self.robot.setTaskCompletedCallback(self._onTaskCompleted)

        signal.signal(signal.SIGTERM, self._stop)
        signal.signal(signal.SIGINT, self._stop)

        xmppLogTarget = XMPPLogTarget()
        xmppLogTarget.setLogReceivedCallback(self._logReceived)
        q.logger.logTargetAdd(xmppLogTarget)

    def _stop(self, signum, frames):
        self.stop()

    def _registerAccounts(self, accountSections):
        """
        Registers all the accounts

        Handles all the accounts at once to use only a global timeout period instead of timeout for each anonymous account
        """
        mappers = dict()
        finished = dict()
        messageIdToJid = dict()
        agentConfigFile = q.config.getInifile('agent_accounts')
        accountSectionDicts = map(lambda section: section.values()[0], accountSections)
        jidToAgentcontroller = dict(map(lambda section: ("%s@%s"%(section.get('agentname'), section.get('domain')), "%s@%s"%(section.get('agentcontrollername'), section.get('domain'))), accountSectionDicts))#create {jid: agentcontrolerjid}
        jidToSectionName = dict(map(lambda item: ("%s@%s"%(item[item.keys()[0]].get('agentname'), item[item.keys()[0]].get('domain')), item.keys()[0]), accountSections)) #create {jid : sectionName}
        def _messagesReceived(id, xmppMessages):
            resultMessage = xmppMessages[-1]
            q.logger.log('result message is received %s'% resultMessage, 5)
            finished[id] = True
            if resultMessage.returncode == '0':
                q.logger.log('account %s registered successfully'%messageIdToJid[id], 5)
                agentConfigFile.setParam(jidToSectionName[messageIdToJid[id]], 'anonymous', 0)
            else:
                q.logger.log('Failed to register agent %s'%messageIdToJid[id], 5)
        countID = 0
        send_retries = dict()
        for jid, client in self.accounts.items():
            if not client.anonymous:
                continue

            client.connect(self._servers[jid])
            mappers[jid] = TaskCallbackMapper(client)
            countID += 1
            messageid = str(countID)
            finished[messageid] = False
            mappers[jid].registerTaskCallback(messageid, _messagesReceived)
            sent_messageid = client.sendMessage(XMPPCommandMessage(jid, jidToAgentcontroller[jid], '', messageid, 'domaincontroller', subcommand='register', params={'params':[client.username, client.password, client.domain],  'options': []}))
            if sent_messageid is None :
               send_retries[jid] = messageid 
            messageIdToJid[messageid] = jid
            
        timeout = self.timeout
        while timeout and filter(lambda item: not item, finished.values()):
            for jid in send_retries.keys():
                messageid = send_retries[jid]
                client = self.accounts[jid]
                sent_messageid = client.sendMessage(XMPPCommandMessage(jid, jidToAgentcontroller[jid], '', messageid, 'domaincontroller', subcommand='register', params={'params':[client.username, client.password, client.domain],  'options': []}))
                if sent_messageid is not None:
                    del send_retries [jid]
                else: 
                    q.logger.log( "Failed to send register message" )
                
            time.sleep(1)
            timeout -= 1
            
        if not timeout:
            
            q.logger.log('timeout occurred while registering agents, status: %s'%map(lambda id: {messageIdToJid[id]: finished[id]}, finished))
            msg_f = "Agent registration failed for %s"
            failed_msg_ids = filter( lambda x: not finished[x], finished.keys() )
            for msg_id in failed_msg_ids :
                jid = messageIdToJid[msg_id]
                msg = msg_f % jid 
                
                tags = q.base.tags.getObject()
                tags.tagSet('login', jid )
                q.errorconditionhandler.raiseCritical( msg, typeid='SSO-AGENT-0002',tags=tags.tagstring,escalate=True)
                
        if filter(lambda item: item, finished.values()):
            self.reloadConfig(registerAnonymous=False)

    def reloadConfig(self, registerAnonymous=True):
        """
        """
        def createLambda(f, *args,**kwargs):
            return lambda: f(*args,**kwargs)

        def reloadPassword( section ):
            cfg = q.config.getConfig('agent_accounts')
            return cfg[section]['password']
                
        if not 'agent' in q.config.list() or not 'agent_accounts' in q.config.list() or not 'agent_acls' in q.config.list():
            raise RuntimeError('Agent config file %s does not exist')


        sections = q.config.getConfig('agent')
        self.timeout = int(sections['main'].get('registeration_timeout', 10))


        accountSections =  q.config.getConfig('agent_accounts')#filter(lambda x: x.startswith('account_'), sections)
        aclSections = q.config.getConfig('agent_acls')
        for accountSection in accountSections:
            sectionInfo = accountSections[accountSection]
            jid = "%s@%s"%(sectionInfo.get('agentname'), sectionInfo.get('domain'))
            isAnonymous = sectionInfo.get('anonymous', False)
            anonymous = True if isAnonymous == '1' or isAnonymous == 'True' else False
            client = XMPPClient(jid, sectionInfo.get('password'), anonymous=anonymous, getPassword = createLambda(reloadPassword, accountSection) )
            
            self.acl[jid] = AgentACL(sectionInfo.get('agentname'), sectionInfo.get('domain'), map(lambda x: aclSections[x], filter(lambda x: aclSections[x].get('account_name') == accountSection, aclSections)))
            self._servers[jid] = sectionInfo.get('server')
            # register the required events
            client.setCommandReceivedCallback(self._onCommandReceived)
            client.setLogReceivedCallback(self._onLogReceived)
            client.setErrorReceivedCallback(self._onErrorReceived)
            client.setResultReceivedCallback(self._onResultReceived)
            client.setMessageReceivedCallback(self._onMessageReceived)
            if self.accounts.has_key(jid) and self.accounts[jid] is not None :
                self.accounts[jid].disconnect()
            self.accounts[jid] = client
            enabled = sectionInfo.get('enabled')
            self._isEnabled[jid] = True if enabled == '1' or enabled == 'True' else False
        if registerAnonymous:
            self._registerAccounts(map(lambda x: {x:accountSections[x]},  accountSections))


    def modifyPassword(self, jid, newPasswd):
        """
        Change the password of given account

        @param jid: JID of the account to change password
        @param newPasswd: new password to set
        """
        if not jid in self.accounts:
            q.logger.log('Account %s does not exist'% jid, 4)
            return
        if not self._isEnabled[jid]:
            q.logger.log('Account %s is not enabled'% jid, 4)
            return
        messageIdToJid = dict()
        agentConfigFile = q.config.getInifile('agent_accounts')
        accountSections = q.config.getConfig('agent_accounts')
        accountSectionDicts = map(lambda section: section.values()[0], map(lambda x: {x:accountSections[x]},  accountSections))
        jidToAgentcontroller = dict(map(lambda section: ("%s@%s"%(section.get('agentname'), section.get('domain')), \
                                                         "%s@%s"%(section.get('agentcontrollername'), section.get('domain'))), accountSectionDicts))#create {jid: agentcontrolerjid}

        a = accountSections 
        jidToSectionName = dict(map(lambda item: ("%s@%s"%(a[item].get('agentname'), a[item].get('domain')), item), accountSections)) #create {jid : sectionName}
     
	passwordChangedInConfig = False   
        def _passwordChanged(id, xmppMessages):
            resultMessage = xmppMessages[-1]
            if resultMessage.returncode == '0':
                q.logger.log('password changed successfully', 5)
                agentConfigFile.setParam(jidToSectionName[messageIdToJid[id]], 'password', newPasswd)
                passwordChangedInConfig = True
            else:
                q.logger.log('Failed to register agent password for %s'%messageIdToJid[id], 5)

        client = self.accounts[jid]
        client.connect(self._servers[jid])
        caller = TaskCallbackMapper(client)
        messageid = '9'
        messageIdToJid[messageid] = jid
        caller.registerTaskCallback(messageid, _passwordChanged)
        
        sentMsgId = None
        timeout = self.timeout 
        while ( sentMsgId is None and timeout ) :
            q.logger.log( "Sending setpasswd msg" )
            sentMsgId = client.sendMessage(XMPPCommandMessage(jid, jidToAgentcontroller[jid], '', messageid, 'domaincontroller', \
                                                          subcommand='setpasswd', params={'params':[client.username, client.password, client.domain, newPasswd], \
                                                                                         'options': []}))
            if sentMsgId is None:
                q.logger.log( "Could not send message. Retrying in 1 sec" )
                time.sleep(5.0)
                timeout -= 5

        if ( sentMsgId is None ) :
            q.logger.log( "Could not send message in a timely manner" )

        timeout = self.timeout
        while ( not passwordChangedInConfig and timeout ) :
            time.sleep (1.0 )
            timeout -= 1
        #client.disconnect()

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
            q.logger.log('Account %s does not exist'% jid, 4)
            return

        if not self._isEnabled[jid]:
            q.logger.log('Account %s is not enabled'% jid, 4)
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
        for jid in self.accounts:
            if self._isEnabled[jid]:
                self.accounts[jid].connect(self._servers[jid])

    def disconnectAllAccounts(self):
        """
        Disconnects all accounts

        @return:                     True is case all accounts disconnected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        
        
        for jid in self.accounts.keys() :
            if self._isEnabled[jid]:    
                if self.accounts[jid] is None :
                    del self.accounts [jid]
                else :
                    self.accounts[jid].disconnect()
                    del self.accounts [jid]
    
            

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

        timeout = self.timeout 
        sentMsgId = None 
        while ( sentMsgId is None and timeout > 0 ) :   
            sentMsgId = self.accounts[xmppmessage.sender].sendMessage(xmppmessage)
            if sentMsgId is None:
                timeout -= 1
                time.sleep(1.0)
            
	return sentMsgId

    def start(self):
        """
        Starts the agent and connects all enabled accounts automatically

        @return:                     True is case all accounts connected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

        self.connectAllAccounts()
        self._status = q.enumerators.AppStatusType.RUNNING

    def stop(self):
        """
        Stops the agent

        @return:                     True is case all accounts disconnected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        q.logger.log( "Stopping agent" )
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
    
    def getConnectionInfo(self):
        
        connection_info = {}
        for jid, client in self.accounts.iteritems():
            agent_info = {}
            agent_info['jid'] = client.jid
            agent_info['username'] = client.username
            agent_info['domain'] = client.domain
            agent_info['status'] = client.status
            agent_info['anonymous'] = client.anonymous
            agent_info['autoreconnect'] = client.autoreconnect
            
            connection_info[jid] = agent_info
            
        return connection_info

    def _onCommandReceived(self, xmppCommandMessage):
        """
        # Check for which account message is
        # Ask robot which tasklets match
        # Check ACL for corresponding account if sender is authorized to execute command on this agent
        # Instruct robot to execute command

        REMARK!
        ## Kill and stop are exceptions, the should call killTask or stopTask on robot
        """
        q.logger.log('Command Message is received: %s'% xmppCommandMessage.format(), 5)

        jid = xmppCommandMessage.sender
        if not xmppCommandMessage.receiver in self.acl:
            q.logger.log('Account %s has no ACLs, command ignored'% xmppCommandMessage.receiver, 4)
            return

        tags = [xmppCommandMessage.command]
        if xmppCommandMessage.subcommand:
            tags.append(xmppCommandMessage.subcommand)

        try:
            commandPaths = self.robot.findCommands(tuple(tags))
            if not commandPaths:
                q.logger.log('No command path found for command:%s, subcommand:%s'%(xmppCommandMessage.command, xmppCommandMessage.subcommand))

            for commandPath in commandPaths:
                if not self.acl[xmppCommandMessage.receiver].isAuthorized(jid, commandPath):
                    q.logger.log('[%s] is not authorized to execute this command:%s'%(jid, commandPath))
                    return

            # get the tasknumber from the xmppCommandMessage if any, otherwise generate one from the robot
            idOption = filter(lambda x: x[:4] == '-id ', xmppCommandMessage.params['options'])
            if idOption:
                tasknumber = idOption[0][4:]
                xmppCommandMessage.messageid = tasknumber
            elif xmppCommandMessage.messageid:
                tasknumber = xmppCommandMessage.messageid
            else:
                tasknumber = self.robot.getNextTaskNumber()

            if xmppCommandMessage.command.lower() == 'killtask':
                taskToBeKilled = xmppCommandMessage.params['params'][0]
                result = self.robot.killTask(taskToBeKilled)
                self.sendMessage(XMPPResultMessage(xmppCommandMessage.receiver, xmppCommandMessage.sender, xmppCommandMessage.resource, xmppCommandMessage.messageid, tasknumber, 0 if result else 1, ''))
            elif xmppCommandMessage.command.lower() == 'stoptask':
                taskToBeStooped = xmppCommandMessage.params['params'][0]
                result = self.robot.stopTask(taskToBeStooped)
                self.sendMessage(XMPPResultMessage(xmppCommandMessage.receiver, xmppCommandMessage.sender, xmppCommandMessage.resource, xmppCommandMessage.messageid, tasknumber, 0 if result else 1, ''))
            else:
                params = xmppCommandMessage.params
                params['agentid'] = xmppCommandMessage.receiver

                self._tasknumberToClient[tasknumber] = (xmppCommandMessage.receiver, xmppCommandMessage.sender, xmppCommandMessage.resource, xmppCommandMessage.messageid)

                self.sendMessage(XMPPTaskNumberMessage(sender = xmppCommandMessage.receiver, receiver = xmppCommandMessage.sender, resource = xmppCommandMessage.resource, messageid = xmppCommandMessage.messageid, tasknumber = tasknumber))
                self.robot.execute(tags, params, tasknumber)

        except Exception, ex:
            q.logger.log('Exception Occurred while trying to execute the command %s'%ex)


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
        self.sendMessage(XMPPResultMessage(sender, receiver, resource, messageid, tasknumber, returncode, returnvalue))
        del self._tasknumberToClient[tasknumber]

    def _onPrintReceived(self, tasknumber, string):
        if not string.strip():
            return
        q.logger.log('Task %s prints: %s'%(tasknumber,string))
        sender, receiver, resource, messageid = self._tasknumberToClient[tasknumber]
        self.sendMessage(XMPPLogMessage(sender, receiver, resource, messageid, tasknumber, string))

    def _onExceptionReceived(self, tasknumber, type_, value, tb):
        q.logger.log('Task %s throws: %s'%(tasknumber,traceback.format_exception(type_, value, tb)))
        sender, receiver, resource, messageid = self._tasknumberToClient[tasknumber]
        self.sendMessage(XMPPLogMessage(sender, receiver, resource, messageid, tasknumber, "Exception: %s"%traceback.format_exception(type_, value, tb)))


    def _logReceived(self, message, tasknumber, level):
        """
        Construct log message from a given message and tasknumber and send it to the appropriate client

        @param message: the message of the log
        @param tasknumber: the number of the task that produced the log
        @param level: verbosity level of the message
        """

#        q.logger.log('[AGENT] Received a log message %s from task %s'%(message, tasknumber), 5)

        (receiver, sender, resource, messageid) = self._tasknumberToClient[tasknumber]
        self.sendMessage(XMPPLogMessage(receiver, sender, resource, messageid, tasknumber, message))

