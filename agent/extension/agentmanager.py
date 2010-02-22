'''
INCUBAID BSD version 2.0 
Copyright (c) 2010 Incubaid BVBA

All rights reserved. 
 
Redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following 
conditions are met: 
 
* Redistributions of source code must retain the above copyright 
notice, this list of conditions and the following disclaimer. 

* Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in    the documentation and/or other materials provided with the   distribution. 
* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
 
THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

PyLabs agent manager module
'''

from pymonkey import i, q
import time

class AgentManager(object):
    '''
    Class which is used by PyLabs extension to start and stop the agent
    '''
    def __init__(self):
        '''
        Constructor
        
        '''
        
        self._pythonBinPath = q.system.fs.joinPaths(q.dirs.binDir, 'python')
        self._agentRunnerPath = q.system.fs.joinPaths(q.dirs.appDir, 'agent', 'lib', 'agentrunner.py')
        self._agentCommand = '%s %s'%(self._pythonBinPath, self._agentRunnerPath)
        self._agentPidFile = q.system.fs.joinPaths(q.dirs.pidDir, 'agent.pid')
        self._timeout = 10
    
    def start(self):
        """
        Starts the agent as a daemon.
    
        @return:                     True if the agent process started succefully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

        """
        Implementation tip:
        -------------------
        * Use following library to run agent as daemon 
        *** -> http://pypi.python.org/pypi/python-daemon/
        """
        if self.getStatus() == q.enumerators.AppStatusType.RUNNING:
            q.console.echo('Agent is already running...')
            return True
        timeout = self._timeout
        startCommand = '%s start'%self._agentCommand
        _, _ = q.system.process.execute(startCommand, outputToStdout = False)
        agentPid = int(open(self._agentPidFile, 'r').read())
        while timeout:
            if q.system.process.isPidAlive(agentPid):
                return True
            time.sleep(1)
            timeout -= 1
        
        if not timeout:
            q.console.echo('Failed to start the server in %s seconds'%self._timeout)
            return False
        
    def stop(self):
        """
        Stops the agent daemon.
        
        @return:                     True if the agent process stopped successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        if self.getStatus() == q.enumerators.AppStatusType.HALTED:
            q.console.echo('Agent is not running...')
            return True
        
        agentPid = int(open(self._agentPidFile, 'r').read())
        timeout = self._timeout
        stopCommand = '%s stop'%self._agentCommand
        _, _ = q.system.process.execute(stopCommand, outputToStdout = False)
        while timeout:
            if not q.system.process.isPidAlive(agentPid):
                return True
            time.sleep(1)
            timeout -= 1
        
        if not timeout:
            q.console.echo('Failed to stop the server in %s seconds'%self._timeout)
            return False

    def getStatus(self):
        """
        Gets the status of the agent
        
        @return:                     Returns q.enumerators.AppStatusType
        @rtype:                      q.enumerators.AppStatusType

        @raise e:                    In case an error occurred, exception is raised
        """
        if not q.system.fs.exists(self._agentPidFile):
            return q.enumerators.AppStatusType.HALTED
        agentPid = int(open(self._agentPidFile, 'r').read())
        return q.enumerators.AppStatusType.RUNNING if q.system.process.isPidAlive(agentPid) else q.enumerators.AppStatusType.HALTED
        