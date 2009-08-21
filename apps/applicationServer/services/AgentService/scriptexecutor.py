from pymonkey import q

import sys, yaml
from subprocess import Popen, PIPE
from twisted.internet import reactor

PYTHON_BIN = '/opt/qbase3/bin/python2.5'
SCRIPT_WRAPPER_PY = '/opt/qbase3/apps/applicationServer/services/AgentService/scriptwrapper.py'

KILL_BIN = '/bin/kill'

class ScriptExecutor:
    
    def __init__(self):
        self.scriptDoneCallback = None
        self.scriptDiedCallback = None
        self._processManager = ProcessManager()
        self._checkProgress()
    
    def setScriptDoneCallback(self, callback):
        self.scriptDoneCallback = callback
        
    def setScriptDiedCallback(self, callback):
        self.scriptDiedCallback = callback
        
    def execute(self, fromm, jobguid, params, script):
        if self._processManager.hasJob(fromm, jobguid):
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + jobguid + "' already exists: skipping the job", 3)
        else:
            wrapper_input = {'params':params, 'script':script}
            yaml_wrapper_input = yaml.dump(wrapper_input)
            proc = Popen([PYTHON_BIN, SCRIPT_WRAPPER_PY], stdout=PIPE, stdin=PIPE)
            self._processManager.addProcess(proc, fromm, jobguid)
            proc.stdin.write(yaml_wrapper_input)
            proc.stdin.close()
    
    def stop(self, fromm, jobguid):
        if self._processManager.hasJob(fromm, jobguid):
            proc = self._processManager.getProcess(fromm, jobguid)
            Popen([KILL_BIN, str(proc.pid)])
        else:
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + jobguid + "' does not exist: cannot stop the job", 3)
    
    def kill(self, fromm, jobguid):
        if self._processManager.hasJob(fromm, jobguid):
            proc = self._processManager.getProcess(fromm, jobguid)
            Popen([KILL_BIN, '-9', str(proc.pid)])
        else:
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + jobguid + "' does not exist: cannot kill the job", 3)
    
    def getJob(self, pid):
        return self._processManager.getJob(pid)
    
    def _checkProgress(self):
        for proc in self._processManager.listRunningProcesses():
            proc_error_code = proc.poll()
            if proc_error_code <> None:
                (fromm, jobguid) = self._processManager.getJob(proc.pid)
                output = proc.stdout.read()
                
                errorOutput = None
                
                if proc_error_code <> 0:
                    errorOutput = "RECEIVED WRONG ERROR CODE FROM WRAPPER: \n" + output
                else:
                    index = output.rfind('\n---\n')
                    if index == -1:
                        errorOutput = "WRAPPER EXITED BEFORE WRITING OUTPUT: \n" + output
                    else:
                        try:
                            yaml_output = output[index+5:]
                            output_object = yaml.load(yaml_output)
                        except:
                            errorOutput = "ERROR WHILE PARSING THE WRAPPER OUTPUT: \n" + output
                        else:
                            if 'errormessage' in output_object:
                                errorOutput = "WRAPPER CAUGHT EXCEPTION IN SCRIPT: \n" + output_object['errormessage']
                            else:
                                params = output_object['params']
                                self.scriptDoneCallback and self.scriptDoneCallback(fromm, jobguid, params)

                if errorOutput <> None:
                    self.scriptDiedCallback and self.scriptDiedCallback(fromm, jobguid, proc_error_code, errorOutput)

                self._processManager.processStopped(proc)
                reactor.callLater(2, self._processManager.removeProcess, proc) #Keep it alive for 2 seconds in case logging comes late.
                     
        reactor.callLater(0.1, self._checkProgress)

class NoSuchJobException(Exception):
    def __init__(self):
        Exception.__init__(self, "No such job")

class ProcessManager:
    
    def __init__(self):
        self.__runningProcesses = []
        self.__pidMapping = {}
        self.__jobMapping = {}
    
    def addProcess(self, proc, fromm, jobguid):
        self.__runningProcesses.append(proc)
        procInfo = (proc, fromm, jobguid)
        self.__pidMapping[proc.pid] = procInfo
        self.__jobMapping[self.__getJobId(fromm, jobguid)] = procInfo
    
    def processStopped(self, proc):
        '''
        The process has stopped: remove it from the process list, but keep the mapping (in case a log comes in late).
        '''
        self.__runningProcesses.remove(proc)
    
    def removeProcess(self, proc):
        '''
        Remove the process completely: remove the mapping.
        '''
        procInfo = self.__pidMapping.pop(proc.pid)
        self.__jobMapping.pop(self.__getJobId(procInfo[1], procInfo[2]))
    
    def listRunningProcesses(self):
        return self.__runningProcesses 
    
    def hasJob(self, fromm, jobguid): 
        return self.__getJobId(fromm, jobguid) in self.__jobMapping
    
    def getProcess(self, fromm, jobguid):
        return self.__jobMapping.get(self.__getJobId(fromm, jobguid))[0]
    
    def getJob(self, pid):
        if self.__pidMapping.get(pid) <> None:
            return self.__pidMapping.get(pid)[1:]
        else:
            return None
        
    def __getJobId(self, fromm, jobguid):
        return fromm + '@' + jobguid;
