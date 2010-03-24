# -*- coding: utf-8 -*-
'''
INCUBAID BSD version 2.0 
Copyright � 2010 Incubaid BVBA

All rights reserved. 
 
Redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following 
conditions are met: 
 
* Redistributions of source code must retain the above copyright 
notice, this list of conditions and the following disclaimer. 

* Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in    the documentation and/or other materials provided with the   distribution. 

* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
 
THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 


PyLabs scheduler service runner
'''

from pymonkey.InitBaseCore import q
import sys
import SimpleXMLRPCServer

from schedulerapi import SchedulerAPI
from scheduler import Scheduler

def setupHandler(handler, api):
    """
    This function registers the methods of the Scheduler API as functions of an XML-RPC handler
    """
    
    #register the standard functions used by the XML-RPC to advertise which methods are available on a given server
    handler.register_introspection_functions()
    
    handler.register_function(api.start, 'scheduler.start')
    handler.register_function(api.stop, 'scheduler.stop')
    handler.register_function(api.getStatus, 'scheduler.getStatus')
    handler.register_function(api.getUpTime, 'scheduler.getUpTime')
    handler.register_function(api.getParams, 'scheduler.getParams')
    
port = int(sys.argv[-1])
handler = SimpleXMLRPCServer.SimpleXMLRPCServer(('0.0.0.0', port))

scheduler = Scheduler()
api = SchedulerAPI(scheduler)

setupHandler(handler, api)

handler.serve_forever()