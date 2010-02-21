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


import unittest
import sys, os
from mock import Mock
from pymonkey import q, i

parentFolder = q.system.fs.getDirName(__file__)[:-1]
sys.path.append(q.system.fs.joinPaths(parentFolder[:parentFolder.rindex(os.sep)], 'lib'))

from xmppclient import *

class dummyConnection:
    _sock = sys.stdin

class XMPPMessageHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.commandMessage0 = """!agent register
param0
$-option0
$param1
$param2
$-option1
$param3\n!"""

        self.commandMessage1 = """!agent register
param0
!
"""
        self.logMessage0 = '@232|logEntry'
        self.resultMessage0 = """!!!3 0
\n!!!"""                
        self.resultMessage1 = """!!!44 8
some error message\n!!!"""

        self.tasknumberMessage0 = '<ID>32'
        
        self.sender = 'testSender'
        self.receiver = 'testReceiver'
        self.messageid = '2'
        
    def testCommandMessage(self):
        commandObject0 = self.xmppMessageHandler.deserialize(self.sender, self.receiver, self.messageid, self.commandMessage0)
        self.xmppMessageHandler.serialize(commandObject0)
        
        commandObject1 = self.xmppMessageHandler.deserialize(self.sender, self.receiver, self.messageid, self.commandMessage1)
        self.xmppMessageHandler.serialize(commandObject1)
        
        q.console.echo('testCommandMessage ... OK')
        
    def testLogMessage(self):
        logObject0 = self.xmppMessageHandler.deserialize(self.sender, self.receiver, self.messageid, self.logMessage0)
        self.xmppMessageHandler.serialize(logObject0)
        
        q.console.echo('testLogMessage ... OK')
        
    def testResultMessage(self):
        resultObject0 = self.xmppMessageHandler.deserialize(self.sender, self.receiver, self.messageid, self.resultMessage0)
        self.xmppMessageHandler.serialize(resultObject0)
        
        resultObject1 = self.xmppMessageHandler.deserialize(self.sender, self.receiver, self.messageid, self.resultMessage1)
        self.xmppMessageHandler.serialize(resultObject1)
        
        q.console.echo('testResultMessage ... OK')
        
    def testTasknumberMessage(self):
        tasknumberObject0 = self.xmppMessageHandler.deserialize(self.sender, self.receiver, self.messageid, self.tasknumberMessage0)
        self.xmppMessageHandler.serialize(tasknumberObject0)
        
        q.console.echo('testTasknumberMessage ... OK')    
        
    def runTest(self):
        self.xmppMessageHandler = XMPPMessageHandler()
        self.testCommandMessage()
        self.testLogMessage()
        self.testResultMessage()
        self.testTasknumberMessage()


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
    
    
class XMPPClientTestCase(unittest.TestCase):
    def setUp(self):
        self.xmppClient = XMPPClient('test@testDomain', 'test')
        self.initialize()        
    def initialize(self):
        
        self.client = dummyClient()
        self.client.connect = Mock(return_value=True)
        self.client.auth = Mock()
        self.client.RegisterHandler = Mock()
        self.client.Process = Mock()
        self.client.disconnect = Mock()
        self.client.send = Mock()
        self.client.connected = True
        self.xmppClient._client = self.client        
        
    def testConnect(self):
        """
        testing the connect method
        """
        self.initialize()
                
        self.xmppClient.connect('localhost')        
        self.assertEquals(self.client.connect.call_count, 1, " XMPPClient.connect() called incorrect number of times:%s"%self.client.connect.call_count)
        self.assertEquals(self.client.auth.call_count, 1, " XMPPClient.auth() called incorrect number of times:%s"%self.client.auth.call_count)
        self.assertEquals(self.client.send.call_count, 0, " XMPPClient.send() called incorrect number of times:%s"%self.client.send.call_count)
        self.assertEquals(self.client.RegisterHandler.call_count, 2, " XMPPClient.RegisterHandler() called incorrect number of times:%s"%self.client.RegisterHandler.call_count)
        self.xmppClient.disconnect()
        
        q.console.echo('testConnect ... OK')
        
    def testConnectTwice(self):
        self.initialize()
        self.client.connected = True
                
        self.xmppClient.connect('localhost')        
        self.xmppClient.connect('localhost')
        self.assertEquals(self.client.connect.call_count, 1, " XMPPClient.connect() called incorrect number of times:%s"%self.client.connect.call_count)
        self.assertEquals(self.client.auth.call_count, 1, " XMPPClient.auth() called incorrect number of times:%s"%self.client.auth.call_count)
        self.assertEquals(self.client.send.call_count, 0, " XMPPClient.send() called incorrect number of times:%s"%self.client.send.call_count)
        self.assertEquals(self.client.RegisterHandler.call_count, 2, " XMPPClient.RegisterHandler() called incorrect number of times:%s"%self.client.RegisterHandler.call_count)
        self.xmppClient.disconnect()        

        q.console.echo('testConnectTwice ... OK')
        
    def testDisconnect(self):
        """
        testing the disconnect method
        """
        self.initialize()     
        self.xmppClient.connect('localhost')   
        self.xmppClient.disconnect()        
        self.assertEquals(self.client.disconnect.call_count, 1, " XMPPClient.disconnect() called incorrect number of times:%s"%self.client.disconnect.call_count)
        
        q.console.echo('testDisconnect ... OK')
        
    def testDisconnectOnDisconnectedClient(self):
        self.initialize()        
        self.xmppClient.connect('localhost')
        self.xmppClient.disconnect()        
        self.xmppClient.disconnect()
        self.assertEquals(self.client.disconnect.call_count, 1, " XMPPClient.disconnect() called incorrect number of times:%s"%self.client.disconnect.call_count)
        
        q.console.echo('testDisconnectOnDisconnectedClient ... OK')
        
    def testSendMessage(self):
        """
        testing the sendMessage method
        """
        self.initialize()        
        self.xmppClient.connect('localhost')
        self.xmppClient.sendMessage(dummyXMPPMessage())
        self.xmppClient.disconnect()        
        self.assertEquals(self.client.send.call_count, 1, " XMPPClient.send() called incorrect number of times:%s"%self.client.send.call_count)
        
        q.console.echo('testSendMessage ... OK')
        
    def testSendMessageOnDisconnectedClient(self):
        self.initialize()        
        self.xmppClient.connect('localhost')
        self.xmppClient.disconnect()
        self.assertRaises(RuntimeError, self.xmppClient.sendMessage, dummyXMPPMessage)

        self.assertEquals(self.client.connect.call_count, 1, " XMPPClient.connect() called incorrect number of times:%s"%self.client.connect.call_count)
        self.assertEquals(self.client.auth.call_count, 1, " XMPPClient.auth() called incorrect number of times:%s"%self.client.auth.call_count)
        self.assertEquals(self.client.send.call_count, 0, " XMPPClient.send() called incorrect number of times:%s"%self.client.send.call_count)
        self.assertEquals(self.client.RegisterHandler.call_count, 2, " XMPPClient.RegisterHandler() called incorrect number of times:%s"%self.client.RegisterHandler.call_count)
        self.assertEquals(self.client.disconnect.call_count, 1, " XMPPClient.disconnect() called incorrect number of times:%s"%self.client.disconnect.call_count)
        
        q.console.echo('testSendMessageOnDisconnectedClient ... OK')
            
    def runTest(self):
        self.testConnect()       
        self.testConnectTwice() 
        self.testSendMessage()
        self.testSendMessageOnDisconnectedClient()
        self.testDisconnect()
        self.testDisconnectOnDisconnectedClient()
        
        
class Test():
    def performTest(self):        
        xmppMessageHandlerTest = XMPPMessageHandlerTestCase()
        xmppClientTest = XMPPClientTestCase()        
        
        runner = unittest.TextTestRunner()
        runner.run(xmppMessageHandlerTest)
        runner.run(xmppClientTest)
        
        

