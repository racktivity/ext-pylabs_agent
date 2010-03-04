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

"""
Log target for sending the messages through xmpp 
"""

from pymonkey import q
from pymonkey.logging.LogObject import LogObject

import threading

class XMPPLogTarget(object):
    def __init__(self, maxVerbosityLevel=7):
        self.enabled = True
        self.maxVerbosityLevel = maxVerbosityLevel

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        True

    def __str__(self):
        return 'XMPPLogTarget'

    def ___repr__(self):
        return str(self)
    
    def _decodeMessage(self, message):
        """
        decode the old pylabas message format, used here as a fallback
        
        @param message: message formated with the old pylabas format: format of log message see: http://bitbucket.org/despiegk/ssospecs/src/tip/1.1/concepts/EventManagement/1. pylabsLogEventMgmt.wiki
        """
        (logtype, now, source, level, tags, messageBody) = message.split('|', 5)
        source = source.strip().replace("/n", "\r\n").replace("/n", "\n").replace("/|", "|").replace("/:", ":")
        messageBody = str(messageBody).strip().replace("/n", "\r\n").replace("/n", "\n").replace("/|", "|").replace("/:", ":")
        tags = str(tags).strip().replace("/n", "\r\n").replace("/n", "\n").replace("/|", "|")
        return (logtype, now, source, level, tags, messageBody)

    def log(self, message):
#        logmsg = LogObject(message)        
#        tags = q.base.tags.getObject(logmsg.tags)
        _, _, _, level, tags, messageBody = self._decodeMessage(message)
        tags = q.base.tags.getObject(tags)
        tasknr = 0
        if tags.tagExists('tasknumber'):
            tasknr = int(tags.tagGet('tasknumber'))
        elif hasattr(threading.currentThread(),  'tasknumber'):
            tasknr = threading.currentThread().tasknumber        
        if tasknr and self._logReceivedCallback:
            self._logReceivedCallback(messageBody, tasknr, level)
        
        return True
    
    def setLogReceivedCallback(self, callback):
        """
        Sets a log received callback
        
        @param callback: python callable object the will be invoked when log received
        """
        
        self._logReceivedCallback = callback
        
    