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


PyLabs scheduler manager
'''

from pymonkey import q
import time
import signal

class SchedulerManager(object):
    """
    Manager extension class that starts/stops the scheduler process
    """
    
    def __init__(self):
        """
        Initializes the main properties of the scheduler
        """
        
        self._schdulerPidFile = q.system.fs.joinPaths(q.dirs.pidDir, 'scheduler_%(portnumber)s.pid')
        self._pythonBinPath = q.system.fs.joinPaths(q.dirs.binDir, 'python')
        self._schedulerServiceRunnerPath = q.system.fs.joinPaths(q.dirs.appDir, 'agent', 'lib', 'schedulerservicerunner.py')
        self._schedulerServiceCommand = '%s %s'%(self._pythonBinPath, self._schedulerServiceRunnerPath)
        self._schedulerStdOut = q.system.fs.joinPaths(q.dirs.varDir, 'scheduler.out')
        self._schedulerStdErr = q.system.fs.joinPaths(q.dirs.varDir, 'scheduler.err')
    
    def start(self, port = 9999, timeout = 5):
        """
        Starts an xml-rpc server in a daemon mode that will serve the basic method of the scheduler 
        
        @param port: number of the port for the server to listen on
        @type port: integer
        
        @param timout: number of seconds to wait before reporting failing to start the server
        @type timeout: integer
        
        @return: True if success False otherwise  
        """
        
        if self.getStatus() == q.enumerators.AppStatusType.RUNNING:
            q.console.echo('Scheduler service is already running...')
            return True
        _timeout = timeout
        pid = q.system.process.runDaemon('%s %s'%(self._schedulerServiceCommand, port), stdout = self._schedulerStdOut, stderr = self._schedulerStdErr)
        while _timeout and not q.system.process.isPidAlive(pid):
            time.sleep(1)
            _timeout -= 1
        
        if not _timeout:
            q.console.echo('Failed to start the scheduler service in %s seconds'%timeout)
            return False
        q.system.fs.writeFile(self._schdulerPidFile%{'portnumber': port}, str(pid))
        return True
    
    
    def stop(self, timeout = 5):
        """
        Stops the scheduler service
        
        @param timeout: number of seconds to wait before trying to kill the shceduler process abruptly
        @type timeout: integer
        """
        if self.getStatus() == q.enumerators.AppStatusType.HALTED:
            q.console.echo('scheduler service is not running...')
            return True
        schedulerServicePid = int(open(self._schdulerPidFile%{'portnumber': self._portnumber}, 'r').read())
        _timeout = timeout
        q.system.process.kill(schedulerServicePid, signal.SIGTERM)
        while timeout:
            if not q.system.process.isPidAlive(schedulerServicePid):
                return True
            time.sleep(1)
            _timeout -= 1
        
        if not _timeout:
            q.console.echo('Failed to stop the scheduler service in %s seconds, trying to kill the process abruptly '%timeout)
            q.system.process.kill(schedulerServicePid, signal.SIGKILL)
            time.sleep(1)
            return not q.system.process.isPidAlive(schedulerServicePid)
        
    
    def getStatus(self):
        """
        Retrieves the status of the scheduler service
        """
        schedulerPidFileExists = filter(lambda filename: filename.startswith('scheduler_') and filename.endswith('.pid'), map(lambda filepath: q.system.fs.getBaseName(filepath), q.system.fs.listFilesInDir(q.dirs.pidDir)))
    
        if not schedulerPidFileExists:
            return q.enumerators.AppStatusType.HALTED
        schedulerPidFileName = schedulerPidFileExists[0]
        self._portnumber = int(schedulerPidFileName[len('scheduler_'): -len('.pid')])
        schedulerServicePid = int(open(q.system.fs.joinPaths(q.dirs.pidDir ,schedulerPidFileName), 'r').read())
        return q.enumerators.AppStatusType.RUNNING if q.system.process.isPidAlive(schedulerServicePid) else q.enumerators.AppStatusType.HALTED