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
#
#* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
# 
#THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
import mock


import unittest
import pdb

from pymonkey import q
from mock import Mock

# should be able to import the module without doing the following
import sys, os

parentFolder = q.system.fs.getDirName(__file__)[:-1]
sys.path.append(q.system.fs.joinPaths(parentFolder[:parentFolder.rindex(os.sep)], 'lib'))

from agent import Agent

class dummyConnection:
    _sock = sys.stdin

class dummyClient(object):
    Connection = dummyConnection()    
    def connect(self, connectionDetails): # e.g connect((server,port))
        pass
    def auth(self, username, userpassword):
        pass
    def RegisterHandler(self, typeOfHandler, callback):
        pass
    def Process(self, timeout):
        pass
    def disconnect(self):
        pass
    def send(self, message):
        pass
    def sendInitPresence(self):
        pass
    def isConnected(self):
        pass
    
class dummyXMPPMessage(object):
    def __init__(self):
        self.sender = 'sender_1'
        self.receiver = 'receiver_1'
        self.message = 'test Message'
    def __str__(self):
        return self.message
    

class AgentTest(unittest.TestCase):
      
     
    def setUp(self):
        # put the test tasklet
        self.testTaskletDirCreated = False        
        self.testTaskletDir = q.system.fs.joinPaths(q.dirs.appDir, 'agent', 'cmds', 'test')
        self.testTaskletPath = q.system.fs.joinPaths(self.testTaskletDir, 'test.py')
        if not q.system.fs.exists(self.testTaskletDir):
            q.system.fs.createDir(self.testTaskletDir)
            self.testTaskletDirCreated = True
        elif q.system.fs.exists(self.testTaskletPath):
            q.system.fs.moveFile(self.testTaskletPath, '%s.bak'%self.testTaskletPath)            
        q.system.fs.copyFile(q.system.fs.joinPaths(parentFolder, 'agent','test.py'), self.testTaskletPath)
        
        # put the test agent.cfg
        self.agentCfgPath = q.system.fs.joinPaths(q.dirs.cfgDir, 'qconfig', 'agent.cfg')
        self.agentCfgCreated = True 
        if q.system.fs.exists(self.agentCfgPath):
            self.agentCfgCreated = False
            q.system.fs.moveFile(self.agentCfgPath, '%s.bak'%self.agentCfgPath)             
        
        q.system.fs.copyFile(q.system.fs.joinPaths(parentFolder, 'agent','agent.cfg'), self.agentCfgPath)
                
        self.agent = Agent()
        
    def tearDown(self):
        if q.system.fs.exists('%s.bak'%self.testTaskletPath):
            q.system.fs.moveFile('%s.bak'%self.testTaskletPath, self.testTaskletPath)
        
        if self.testTaskletDirCreated:
            q.system.fs.removeDirTree(self.testTaskletDir)
            
        if self.agentCfgCreated:
            q.system.fs.removeFile(self.agentCfgPath)
        else:
            q.system.fs.moveFile('%s.bak'%self.agentCfgPath, self.agentCfgPath)
            
        self.agenCfgPath = None    
        self.testTaskletPath = None
        self.testTaskletDirCreated = False
        self.agentCfgCreated = False
        self.testTaskletDir = None
        del self.agent
        
    def initialize(self):
        
        self.client = dummyClient()
        self.client.connect = Mock(return_value=True)
        self.client.auth = Mock()
        self.client.RegisterHandler = Mock()
        self.client.Process = Mock()
        self.client.disconnect = Mock()
        self.client.send = Mock()
        for jid in self.agent.accounts:
            self.agent.accounts[jid]._client = self.client
            self.agent.accounts[jid]._client.connected = True
        
    def testConnectAccount(self):
        self.initialize()
        self.agent.connectAccount('node0@sso.dass.com')
        
        
        self.assertEquals(self.client.connect.call_count, 1, " XMPPClient.connect() called incorrect number of times:%s"%self.client.connect.call_count)
        self.assertEquals(self.client.auth.call_count, 1, " XMPPClient.auth() called incorrect number of times:%s"%self.client.auth.call_count)
        self.assertEquals(self.client.send.call_count, 0, " XMPPClient.send() called incorrect number of times:%s"%self.client.send.call_count)
        self.assertEquals(self.client.RegisterHandler.call_count, 2, " XMPPClient.RegisterHandler() called incorrect number of times:%s"%self.client.RegisterHandler.call_count)
        
        self.agent.disconnectAccount('node0@sso.dass.com')
        
        q.console.echo('testConnectAccount ... OK')
        
    def testConnectWithDisabledAccount(self):
        self.initialize()
        self.assertFalse(self.agent._isEnabled['node1@domain.com'])
        self.assertRaises(RuntimeError, self.agent.connectAccount, 'node1@domain.com')
        
        q.console.echo('testConnectWithDisabledAccount ... OK')                
    
    def testDisconnectAccount(self):
        self.initialize()
        self.agent.connectAccount('node0@sso.dass.com')
        
        self.assertEquals(self.client.connect.call_count, 1, " XMPPClient.connect() called incorrect number of times:%s"%self.client.connect.call_count)
        self.assertEquals(self.client.auth.call_count, 1, " XMPPClient.auth() called incorrect number of times:%s"%self.client.auth.call_count)
        self.assertEquals(self.client.send.call_count, 0, " XMPPClient.send() called incorrect number of times:%s"%self.client.send.call_count)
        self.assertEquals(self.client.RegisterHandler.call_count, 2, " XMPPClient.RegisterHandler() called incorrect number of times:%s"%self.client.RegisterHandler.call_count)
        
        self.agent.disconnectAccount('node0@sso.dass.com')        
        self.assertEquals(self.client.disconnect.call_count, 1, " XMPPClient.disconnect() called incorrect number of times:%s"%self.client.disconnect.call_count)
        
        q.console.echo('testDisconnectAccount ... OK')
    
    def testConnectAllAccounts(self):
        self.initialize()        
        self.agent.connectAllAccounts()
        
        self.assertEquals(self.client.connect.call_count, 1, " XMPPClient.connect() called incorrect number of times:%s"%self.client.connect.call_count)
        self.assertEquals(self.client.auth.call_count, 1, " XMPPClient.auth() called incorrect number of times:%s"%self.client.auth.call_count)
        self.assertEquals(self.client.send.call_count, 0, " XMPPClient.send() called incorrect number of times:%s"%self.client.send.call_count)
        self.assertEquals(self.client.RegisterHandler.call_count, 2, " XMPPClient.RegisterHandler() called incorrect number of times:%s"%self.client.RegisterHandler.call_count)
        
        q.console.echo('testConnectAllAccounts ... OK')        
    
    def testDisconnectAllAccounts(self):
        
        self.initialize()        
        self.agent.disconnectAllAccounts()
        
        self.assertEquals(self.client.disconnect.call_count, 1, " XMPPClient.disconnect() called incorrect number of times:%s"%self.client.disconnect.call_count)
        
        q.console.echo('testDisconnectAllAccounts ... OK')
            
    def testSendMessage(self):
        self.initialize()
        self.agent.connectAccount('node0@sso.dass.com')
        
        xmppMessage = dummyXMPPMessage()
        xmppMessage.sender = 'node0@sso.dass.com'
        self.agent.sendMessage(xmppMessage)        
        self.assertEquals(self.client.send.call_count, 1, " XMPPClient.send() called incorrect number of times:%s"%self.client.send.call_count)
        
        self.agent.disconnectAccount('node0@sso.dass.com')
        
        q.console.echo('testSendMessage ... OK')        
        
    def testStartAndStop(self):
        self.initialize()
        self.agent.start()
        
        self.assertEquals(self.client.connect.call_count, 1, " XMPPClient.connect() called incorrect number of times:%s"%self.client.connect.call_count)
        self.assertEquals(self.client.auth.call_count, 1, " XMPPClient.auth() called incorrect number of times:%s"%self.client.auth.call_count)
        self.assertEquals(self.client.send.call_count, 0, " XMPPClient.send() called incorrect number of times:%s"%self.client.send.call_count)
        self.assertEquals(self.client.RegisterHandler.call_count, 2, " XMPPClient.RegisterHandler() called incorrect number of times:%s"%self.client.RegisterHandler.call_count)
        self.assertEquals(self.agent.getStatus(), q.enumerators.AppStatusType.RUNNING, "Agent.getStatus() should return RUNNING but it returns %s"%self.agent.getStatus())
        
        self.agent.stop()
        self.assertEquals(self.client.disconnect.call_count, 1, " XMPPClient.disconnect() called incorrect number of times:%s"%self.client.disconnect.call_count)
        self.assertEquals(self.agent.getStatus(), q.enumerators.AppStatusType.HALTED, "Agent.getStatus() should return HALTED but it returns %s"%self.agent.getStatus())
        
        q.console.echo('testStartAndStop ... OK')
    
    def runTest(self):
        self.testConnectAccount()
        self.testConnectWithDisabledAccount()
        self.testDisconnectAccount()
        self.testConnectAllAccounts()
        self.testDisconnectAllAccounts()
        self.testSendMessage()
        # self.testStartAndStop()  #skipped until we reach a method of how to start the stop the agent, e.g. will the start method be blocking?? 
        
