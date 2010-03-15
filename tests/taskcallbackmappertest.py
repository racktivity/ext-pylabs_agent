# -*- coding: utf-8 -*-
#INCUBAID BSD version 2.0 
#Copyright © 2010 Incubaid BVBA
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
import unittest
import sys, os
from pymonkey import q, i
from mock import Mock

parentFolder = q.system.fs.getDirName(__file__)[:-1]
sys.path.append(q.system.fs.joinPaths(parentFolder[:parentFolder.rindex(os.sep)], 'lib'))
sys.path.append(q.system.fs.joinPaths(parentFolder[:parentFolder.rindex(os.sep)], 'agent_service'))

from xmppclient import *
from taskcallbackmapper import TaskCallbackMapper

TYPE_RESULT = 'RESULT'
TYPE_LOG = 'LOG'
TYPE_COMMAND = 'COMMAND'
TYPE_ERROR = 'ERROR'
TYPE_TASKNUMBER = 'TASKNUMBER'
TYPE_UNKNOWN = 'UNKNOWN'

class dummyClient(object):
    def __init__(self):
        self.callbacks = {TYPE_COMMAND:None, TYPE_LOG:None, TYPE_RESULT:None, TYPE_ERROR:None, TYPE_TASKNUMBER:None, TYPE_UNKNOWN:None}
        
    def setCommandReceivedCallback(self, commandHandler):
        """
        @param commandHandler:           Callable which is called whenever a command message is received.
        @type commandHandler:            callable
        @note:                       Interface for the callable must be (XMPPCommandMessage)
        """
        self.callbacks[TYPE_COMMAND] = commandHandler

    def setLogReceivedCallback(self, logHandler):
        """
        @param logHandler:           Callable which is called whenever a log message is received.
        @type logHandler:            callable
        @note:                       Interface for the callable must be (XMPPLogMessage)
        """
        self.callbacks[TYPE_LOG] = logHandler

    def setErrorReceivedCallback(self, errorHandler):
        """
        @param errorHandler:         Callable which is called whenever a error message is received.
        @type errorHandler:          callable
        @note:                       Interface for the callable must be (XMPPErrorMessage)
        
        """
        self.callbacks[TYPE_ERROR] = errorHandler

    def setResultReceivedCallback(self, resultHandler):
        """
        @param resultHandler:        Callable which is called whenever a result message is received.
        @type resultHandler:         callable
        @note:                       Interface for the callable must be (XMPPResultMessage)
        """
        self.callbacks[TYPE_RESULT] = resultHandler
    
    def setTaskNumberReceivedCallback(self, tasknumberHandler):
        """
        @param messageHandler:       Callable which is called whenever a tasknumber message is received.
        @type messageHandler:        callable
        @note:                       Interface for the callable must be (XMPPTaskNumberMessage)
        """
        self.callbacks[TYPE_TASKNUMBER] = tasknumberHandler    
    
    def setMessageReceivedCallback(self, messageHandler):
        """
        @param messageHandler:       Callable which is called whenever a message is received.
        @type messageHandler:        callable
        @note:                       Interface for the callable must be (XMPPMessage)
        """
        self.callbacks[TYPE_UNKNOWN] = messageHandler      
        
class TaskCallbackMapperTestCase(unittest.TestCase):
    
    def init(self):
        self._client = dummyClient()
        self._xmppMessageHandler = XMPPMessageHandler()
        self._taskcallbackmapper = TaskCallbackMapper(self._client)
        self._finished = False
        self._id = '2'
        
    def _finishCallback(self, id, xmppmessages):        
        self._finished = True        
        
    def _sendmessagesWithoutResult(self):
        sender = 'testSender'
        receiver = 'testReceiver'
        messageid = self._id 

        logmessage0 = XMPPLogMessage(sender, receiver, '', messageid, self._id, 'first log') 
        self._client.callbacks[TYPE_LOG](logmessage0)
        
        logmessage1 = XMPPLogMessage(sender, receiver, '', messageid, self._id, 'second log') 
        self._client.callbacks[TYPE_LOG](logmessage1)

    def _sendmessagesWithResult(self):
        sender = 'testSender'
        receiver = 'testReceiver'
        messageid = self._id 

        logmessage0 = XMPPLogMessage(sender, receiver, '', messageid, self._id, 'first log') 
        self._client.callbacks[TYPE_LOG](logmessage0)
        
        logmessage1 = XMPPLogMessage(sender, receiver, '', messageid, self._id, 'second log') 
        self._client.callbacks[TYPE_LOG](logmessage1)
                
        
        resultMessage = XMPPResultMessage(sender, receiver, '', messageid, self._id, 0, '')
        self._client.callbacks[TYPE_RESULT](resultMessage)
        
    def testSuccessfulScenario(self):
        self.init()
        self._taskcallbackmapper.registerTaskCallback(self._id, self._finishCallback)
        self._sendmessagesWithResult()
        self.assertTrue(self._finished, 'messages should be received')
        
    def testUnsuccessfulScenario(self):
        self.init()               
        self._taskcallbackmapper.registerTaskCallback(self._id, self._finishCallback)
        self._sendmessagesWithoutResult()
        self.assertFalse(self._finished, 'messages should not be received')
            
    def runTest(self):
        self.testSuccessfulScenario()
        self.testUnsuccessfulScenario()
        
        

            
