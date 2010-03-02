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


'''
PyLabs Thread Redirector Module
'''

from pymonkey import q
import time
import sys, threading


class ThreadRedirector:
    def __init__(self):        
        self._stream = sys.__stdout__
        self._onPrintReceived = None        
    
    def setOnPrintReceivedCallback(self, handler):
        """
        set the onPrintReceived Callback for the ThreadRedirector
        
        e.g def handler(tasknumber, string):
        """
        self._onPrintReceived = handler
        
    def write(self, string):
        try:
            curThread = threading.currentThread()                
            if hasattr(curThread, 'tasknumber'):
                if self._onPrintReceived:
                    self._onPrintReceived(curThread.tasknumber, string)
                else:
                    q.logger.log('Warning, no callback is registered for onPrintReceived', 5)                        
            else:                    
                sys.__stdout__.write(string)                    
        except Exception, ex:
            q.logger.log('Exception occurred while processing print messages , %s'%ex)
            
    def __getattr__(self, attr):
        return getattr(self._stream, attr)

