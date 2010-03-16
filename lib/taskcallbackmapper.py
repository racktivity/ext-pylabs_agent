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

import xmpp

class TaskCallbackMapper(object):
    def __init__(self, xmppclient):
        self._client = xmppclient 
        self._client.setLogReceivedCallback(self._onGenericMessageReceived)
        self._client.setErrorReceivedCallback(self._onGenericMessageReceived)
        self._client.setTaskNumberReceivedCallback(self._onGenericMessageReceived)
        self._client.setMessageReceivedCallback(self._onGenericMessageReceived)
        
        self._client.setResultReceivedCallback(self._onResultMessageReceived)
        
        self._callbacks = {}
        self._messagesReceived = {}
    
    def _onGenericMessageReceived(self, xmppMessage):
        '''
        call back registed in the agent to be called when some message is called 
        '''
        id = xmppMessage.messageid
        q.logger.log('_onGenericMessageReceived id:%s , on xmppmessage:%s'% (id, xmppMessage), 5)
        
        if not self._messagesReceived.get(id):
            self._messagesReceived[id] = list()
        self._messagesReceived[id].append(xmppMessage)
            
            
    def _onResultMessageReceived(self, xmppMessage):
        id = xmppMessage.messageid
        q.logger.log('_onResultMessageReceived id:%s , on xmppmessage:%s'%(id, xmppMessage), 5)
        self._messagesReceived[id].append(xmppMessage)
        if not self._callbacks.get(id):
            q.logger.log('XMPPMessage %s is received for unknown ID %s'%(id, xmppMessage), 5)
            return
        self._callbacks[id](id, self._messagesReceived[id])
        del self._messagesReceived[id]
        del self._callbacks[id]
    
    
    def registerTaskCallback(self, id, callback):
        self._callbacks[id] = callback    