from pymonkey import q

import sys, yaml
from subprocess import Popen, PIPE
from twisted.internet import reactor

if q.platform.isWindows():
    PYTHON_BIN = q.system.fs.joinPaths(q.dirs.baseDir, 'lib', 'python2.6', 'python.exe')
else:
    PYTHON_BIN = q.system.fs.joinPaths(q.dirs.binDir,'python')
SCRIPT_WRAPPER_PY = q.system.fs.joinPaths(q.dirs.appDir,'applicationserver', 'services', 'agent_service', 'scriptwrapper.py') 

KILL_BIN = '/bin/kill'

class ScriptExecutor:

    def __init__(self, checkProgress=True):
        self.scriptDoneCallback = None
        self.scriptDiedCallback = None
        self._processManager = ProcessManager()
        if checkProgress:
            self._checkProgress()

    def setScriptDoneCallback(self, callback):
        self.scriptDoneCallback = callback

    def setScriptDiedCallback(self, callback):
        self.scriptDiedCallback = callback

    def executeQshellCommand(self, fromm, tasknr, params, script, captureOutput, maxLogLevel):        
        q.logger.log('DEBUG: scriptexecuter.exescute: tasknr:%s, script:%s, params:%s '%(tasknr, script, params))
        try:
            if self._processManager.hasJob(fromm, tasknr):
                q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + tasknr + "' already exists: skipping the job", 3)
            else:            
                params['maxloglevel'] = maxLogLevel
                wrapper_input = {'params':params, 'script':script}
                q.logger.log('DEBUG: before dumping yaml')
                yaml_wrapper_input = yaml.dump(wrapper_input)
                q.logger.log('DEBUG: before spawning new process yaml_input:%s, script:%s, params:%s'%(yaml_wrapper_input, script, params))                
                proc = q.system.process.executeAsync(PYTHON_BIN, args=[SCRIPT_WRAPPER_PY], argsInCommand=False, useShell=False)
                proc.captureOutput = captureOutput
                self._processManager.addProcess(proc, fromm, tasknr)
                proc.stdin.write(yaml_wrapper_input)
                proc.stdin.close()
        except Exception, ex:
            q.logger.log('ERROR: %s'%ex)
            
    def executeShellCommand(self, fromm, tasknr, params, script, captureOutput):        
        q.logger.log('DEBUG: scriptexecuter.executeShellCommand: tasknr:%s, script:%s, params:%s, captureOutput:%s'%(tasknr, script, params, captureOutput))
        try:
            if self._processManager.hasJob(fromm, tasknr):
                q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + tasknr + "' already exists: skipping the job", 3)
            else:
                proc = q.system.process.executeAsync(script, argsInCommand=True)
                proc.captureOutput = captureOutput
                self._processManager.addProcess(proc, fromm, tasknr)
        except Exception, ex:
            q.logger.log('ERROR: %s'%ex)

    def stop(self, fromm, tasknr):
        if self._processManager.hasJob(fromm, tasknr):
            proc = self._processManager.getProcess(fromm, tasknr)
            q.system.process.kill(proc.pid)            
        else:
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + tasknr + "' does not exist: cannot stop the job", 3)

    def kill(self, fromm, tasknr):
        if self._processManager.hasJob(fromm, tasknr):
            proc = self._processManager.getProcess(fromm, tasknr)
            q.system.process.kill(proc.pid)            
        else:
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + tasknr + "' does not exist: cannot kill the job", 3)

    def getJob(self, pid):
        return self._processManager.getJob(pid)

    def _checkProgress(self):       
        try:
            for proc in self._processManager.listRunningProcesses():
                proc_error_code = proc.poll()
                if proc_error_code is None:
                    continue
                
                (fromm, tasknr) = self._processManager.getJob(proc.pid)
                output = proc.stdout.read() if proc.captureOutput else ''
                q.logger.log('DEBUG: checkprogress() output:%s'%output)
                errorOutput = None
                params = dict()
                params['returncode'] = proc_error_code

                if proc_error_code <> 0:                        
                    errorOutput = "RECEIVED WRONG ERROR CODE FROM WRAPPER: \n%s\n%s"%(output, proc.stderr.read() if proc.captureOutput else '')
                else:
                    index = output.rfind('---')
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
                                params.update(output_object['params'])
                                beginindex = 0 or output.find('!!!')
                                params['returnmessage'] = output[beginindex:index]                                
                                self.scriptDoneCallback and self.scriptDoneCallback(fromm, tasknr, params)

                if errorOutput <> None:                    
                    self.scriptDiedCallback and self.scriptDiedCallback(fromm, tasknr, proc_error_code, errorOutput)

                self._processManager.processStopped(proc)
                reactor.callLater(2, self._processManager.removeProcess, proc) #Keep it alive for 2 seconds in case logging comes late.
        except:
            raise
        finally:            
            reactor.callLater(0.1, self._checkProgress)

class NoSuchJobException(Exception):
    def __init__(self):
        Exception.__init__(self, "No such job")

class ProcessManager:

    def __init__(self):
        self.__runningProcesses = []
        self.__pidMapping = {}
        self.__jobMapping = {}

    def addProcess(self, proc, fromm, tasknr):
        self.__runningProcesses.append(proc)
        procInfo = (proc, fromm, tasknr)
        self.__pidMapping[proc.pid] = procInfo
        q.logger.log('DEBUG: Starting process with pid:%s'%proc.pid)
        self.__jobMapping[self.__getJobId(fromm, tasknr)] = procInfo

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

    def hasJob(self, fromm, tasknr):
        return self.__getJobId(fromm, tasknr) in self.__jobMapping

    def getProcess(self, fromm, tasknr):
        return self.__jobMapping.get(self.__getJobId(fromm, tasknr))[0]

    def getJob(self, pid):
        if self.__pidMapping.get(pid) <> None:
            return self.__pidMapping.get(pid)[1:]
        else:
            return None

    def __getJobId(self, fromm, tasknr):
        return fromm + '@' + tasknr;
