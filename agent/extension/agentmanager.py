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
import signal, json

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
        self._agentVarDir = q.system.fs.joinPaths(q.dirs.varDir, 'agent')
        self._agentStdout = q.system.fs.joinPaths(self._agentVarDir, 'stdout')
        self._agentStderr = q.system.fs.joinPaths(self._agentVarDir, 'stderr')
    
    def start(self):
        """
        Starts the agent as a daemon.
    
        @return:                     True if the agent process started succefully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

        """
        Implementation tip: ( didnt use it since it cause some problem with paramiko which used in portforwarding)
        -------------------
        * Use following library to run agent as daemon 
        *** -> http://pypi.python.org/pypi/python-daemon/
        """
        if self.getStatus() == q.enumerators.AppStatusType.RUNNING:
            q.console.echo('Agent is already running...')
            return True
        timeout = self._timeout
#        startCommand = '%s start'%self._agentCommand
#        _, _ = q.system.process.execute(startCommand, outputToStdout = False)        
        pid = q.system.process.runDaemon(self._agentCommand, stdout = self._agentStdout, stderr = self._agentStderr)
        while timeout and not q.system.process.isPidAlive(pid):
#            if q.system.fs.exists(self._agentPidFile):
#                agentPid = int(open(self._agentPidFile, 'r').read())
#                if q.system.process.isPidAlive(agentPid):
#                    return True
            time.sleep(1)
            timeout -= 1
        
        if not timeout:
            q.console.echo('Failed to start the agent in %s seconds'%self._timeout)
            return False
        q.system.fs.writeFile(self._agentPidFile, str(pid))
        return True
        
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
#        stopCommand = '%s stop'%self._agentCommand
#        _, _ = q.system.process.execute(stopCommand, outputToStdout = False)
        q.system.process.kill(agentPid, signal.SIGTERM)
        while timeout:
            if not q.system.process.isPidAlive(agentPid):
                q.system.fs.remove(self._agentPidFile, True)
                return True
            time.sleep(1)
            timeout -= 1
        
        if not timeout:
            q.console.echo('Failed to stop the agent in %s seconds, trying to kill the process abruptly '%self._timeout)
            q.system.process.kill(agentPid, signal.SIGKILL)
            time.sleep(1)
            q.system.fs.remove(self._agentPidFile, True)
            return not q.system.process.isPidAlive(agentPid)

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
    
    def getConnectionInfo(self):
        
        if self.getStatus() != q.enumerators.AppStatusType.RUNNING:
            raise ValueError('Agent is not running')
        
        info_path = q.system.fs.joinPaths(q.dirs.tmpDir, 'agent_connection_info.json')
        q.system.fs.remove(info_path, True)
        
        agentPid = int(open(self._agentPidFile, 'r').read())
        timeout = self._timeout

        info = {}
        
        # SIGRTMIN will dump connection info
        q.system.process.kill(agentPid, signal.SIGRTMIN)
        time.sleep(1)
        
        
        try:
            while timeout:
                if q.system.fs.exists(info_path):
                    info = json.loads(q.system.fs.fileGetContents(info_path))
                    q.system.fs.remove(info_path, True)
                    return info
                
                time.sleep(1)
                # Need to resend signal as signal may be ignored while pm is loading
                q.system.process.kill(agentPid, signal.SIGRTMIN)
                timeout -= 1
        except Exception, ex:
            q.system.fs.remove(info_path, True)
            raise RuntimeError('Error retrieving connection info: %s '  % ex.message)     
            
        q.system.fs.remove(info_path, True)
        q.logger.log('Failed to retrieve connection info',  1)
        
        return info
    
    def restart(self):
        """
        Restart the agent process
        """
        self.stop()
        self.start()
        