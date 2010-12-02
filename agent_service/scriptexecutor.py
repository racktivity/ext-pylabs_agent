from pymonkey import q

import sys, yaml, os
from subprocess import Popen, PIPE
from twisted.internet import reactor
import base64

PYTHON_BIN =  sys.executable

class ScriptExecutor:

    def __init__(self):
        self.scriptDoneCallback = None
        self.scriptDiedCallback = None
        self._processManager = ProcessManager()
        self._checkProgress()
        
        script_path = q.system.fs.joinPaths(q.dirs.tmpDir, 'rscripts')
        if not q.system.fs.exists(script_path):
            q.system.fs.createDir(script_path)

    def setScriptDoneCallback(self, callback):
        self.scriptDoneCallback = callback

    def setScriptDiedCallback(self, callback):
        self.scriptDiedCallback = callback

    def execute(self, fromm, jobguid, params, script):
        if self._processManager.hasJob(fromm, jobguid):
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + jobguid + "' already exists: skipping the job", 3)
        else:
            script = base64.decodestring(script)
            p = str(params)
            
            result_path = self._getScriptResultPath(jobguid)
            error_path  = result_path.replace('.result', '.error') 
            
            script_content = \
            """import sys
from pymonkey.InitBaseCore import q,i

sys.path.append(q.system.fs.joinPaths(q.dirs.appDir, 'applicationserver','services'))
from agent_service.logtarget import AgentLogTarget

agentlog = AgentLogTarget()
q.logger.logTargetAdd(agentlog)

import traceback, time, yaml
import base64

##temporary fix SSOBF-217
import os
os.umask(022)

#### PARAMETERS ####
params = %(params)s
#### /PARAMETERS ####

errormessage = None

#### SCRIPT ####
%(script)s
#### /SCRIPT ####

# Construct the return message
returnobject = {"params":params}
if errormessage:
    returnobject["errormessage"] = errormessage

# Write the result to file
result_file = '%(result_path)s'

q.system.fs.writeFile(result_file, yaml.dump(returnobject))

sys.exit(0)           
""" % {'params': p, 'script': script, 'result_path': result_path}
            
            script_path = self._getScriptPath(jobguid)
            
            q.system.fs.writeFile(script_path, script_content)
           
            with open(error_path, "wb") as out: 
                proc = Popen([PYTHON_BIN, script_path], stdout=out, stdin=None, stderr=out, close_fds=True)
            self._processManager.addProcess(proc, fromm, jobguid)

    def stop(self, fromm, jobguid):
        if self._processManager.hasJob(fromm, jobguid):
            proc = self._processManager.getProcess(fromm, jobguid)
            q.system.process.kill(proc.pid, signal.SIGSTOP)
        else:
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + jobguid + "' does not exist: cannot stop the job", 3)

    def kill(self, fromm, jobguid):
        if self._processManager.hasJob(fromm, jobguid):
            proc = self._processManager.getProcess(fromm, jobguid)
            q.system.process.kill(proc.pid)
        else:
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + jobguid + "' does not exist: cannot kill the job", 3)

    def getJob(self, pid):
        return self._processManager.getJob(pid)
    
    def _getScriptPath(self, jobguid):
        return q.system.fs.joinPaths(q.dirs.tmpDir, 'rscripts', '%s.rscript' % jobguid)

    def _getScriptResultPath(self, jobguid):
        return q.system.fs.joinPaths(q.dirs.tmpDir, 'rscripts', '%s.result' % jobguid)

    def _checkProgress(self):
        for proc in self._processManager.listRunningProcesses():
            proc_error_code = proc.poll()
            if proc_error_code <> None:
                (agentcontrollerguid, jobguid) = self._processManager.getJob(proc.pid)
               
                errorOutput = None
 
                result_path = self._getScriptResultPath(jobguid)
                error_path  = result_path.replace('.result', '.error')

                if not q.system.fs.exists(result_path) or proc_error_code <> 0:
                    errorOutput = "RECEIVED WRONG ERROR CODE FROM WRAPPER: \n"
                    if q.system.fs.exists(error_path):
                        error_output = q.system.fs.fileGetContents(error_path)
                        errorOutput = '\n'.join([errorOutput, error_output])
                else:
                    output = q.system.fs.fileGetContents(result_path)
                    
                    try:
                        output_object = yaml.load(output)
                    except:
                        errorOutput = "ERROR WHILE PARSING THE WRAPPER OUTPUT: \n" + output
                    else:
                        if 'errormessage' in output_object:
                            errorOutput = "WRAPPER CAUGHT EXCEPTION IN SCRIPT: \n" + output_object['errormessage']
                        else:
                            params = output_object['params']
                            self.scriptDoneCallback and self.scriptDoneCallback(agentcontrollerguid, jobguid, params)

                if errorOutput <> None:
                    self.scriptDiedCallback and self.scriptDiedCallback(agentcontrollerguid, jobguid, proc_error_code, errorOutput)

                self._processManager.processStopped(proc)
                reactor.callLater(2, self._processManager.removeProcess, proc) #Keep it alive for 2 seconds in case logging comes late.
                
                script_path = self._getScriptPath(jobguid)
                
                q.system.fs.remove(script_path, onlyIfExists=True)
                q.system.fs.remove(result_path, onlyIfExists=True)
                q.system.fs.remove(error_path, onlyIfExists=True)   

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
