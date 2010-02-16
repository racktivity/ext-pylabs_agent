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



#
#Most of this code is taken from the python recipe on http://code.activestate.com/recipes/496960/
#

import threading
import inspect
import ctypes

def _asyncRaise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble, 
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None) # use None instead of 0 so that it works for 64-bit systems
        raise SystemError("PyThreadState_SetAsyncExc failed")

class KillableThread(threading.Thread):
    """
    Thread class that can be terminated from other thread context
    """
    
    def __init__(self):
        super(KillableThread, self).__init__()
        self._stop = threading.Event()
        
        
    
    def stop(self):
        """
        Sets the stop event flag
        """
        self._stop.set()
    
    
    def stopped(self):
        """
        Checks if the thread is stopped or not
        """
        return self._stop.isSet()
    
        
    def _getCurrentThreadId(self):
        """
        determines the current thread id
        """
        
        if not self.isAlive():
            raise threading.ThreadError('Thread must be active')
        #do we have the thread id cached ?
        if hasattr(self, '_threadId'):
            return self._threadId
        
        #no, look for it in the active dict
        for threadId , threadObj in threading._active.items():
            if threadObj == self:
                self._threadId = threadId
                return self._threadId
        
        raise AssertionError("could not determine the thread's id")
    
    
    def raiseExc(self, excType):
        """
        raises the given exception type in context of the current thread
        """
        _asyncRaise(self._getCurrentThreadId(), excType)
        
    def terminate(self):
        """
        raises a systemExit in the context of the given thread, which should cause the thread to exit silently unless caught
        """
        
        self.raiseExc(SystemExit)
