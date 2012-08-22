from pylabs import q, i

import sys, yaml, os, signal, time, traceback
from twisted.internet import reactor
import base64

PYTHON_BIN =  sys.executable

class Script:
    def __init__(self, script, params, result_path, error_path):
        self.script = script
        self.params = params
        self.result_path = result_path
        self.error_path = error_path

    def run(self):
        # redirect stdout & stderr to error_path
        with open(self.error_path, "wb") as output:
            sys.stdout = output
            sys.stderr = output

            sys.path.append(q.system.fs.joinPaths(q.dirs.appDir, 'applicationserver','services'))
            from agent_service.logtarget import AgentLogTarget

            agentlog = AgentLogTarget()
            q.logger.logTargetAdd(agentlog)

            ##temporary fix SSOBF-217
            os.umask(022)

            errormessage = None

            #### SCRIPT ####
            try:
                # Run the script using the params
                code = compile(self.script.replace("\n\r", "\n"), "<string>", "exec")
                local_ns = { "params": self.params, "q": q, "i": i }
                global_ns = local_ns

                exec(code, global_ns, local_ns)
            except:
                errormessage = traceback.format_exc()
            #### /SCRIPT ####

            # Construct the return message
            returnobject = { "params": self.params }
            if errormessage:
                returnobject["errormessage"] = errormessage

            # Write the result to file
            q.system.fs.writeFile(self.result_path, yaml.dump(returnobject))

        os._exit(0)


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

            result_path = self._getScriptResultPath(jobguid)
            error_path  = result_path.replace('.result', '.error')

            pid = os.fork()
            if pid == 0:
                #child process
                s = Script(script, params, result_path, error_path)
                s.run()
            else:
                #parent process
                self._processManager.addProcess(pid, fromm, jobguid)

    def stop(self, fromm, jobguid):
        if self._processManager.hasJob(fromm, jobguid):
            pid = self._processManager.getProcess(fromm, jobguid)
            q.system.process.kill(pid, signal.SIGSTOP)
        else:
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + jobguid + "' does not exist: cannot stop the job", 3)

    def kill(self, fromm, jobguid):
        if self._processManager.hasJob(fromm, jobguid):
            pid = self._processManager.getProcess(fromm, jobguid)
            q.system.process.kill(pid)
        else:
            q.logger.log("[SCRIPTEXECUTOR] Error: job from '" + fromm + "' with id '" + jobguid + "' does not exist: cannot kill the job", 3)

    def getJob(self, pid):
        return self._processManager.getJob(pid)

    def _getScriptPath(self, jobguid):
        return q.system.fs.joinPaths(q.dirs.tmpDir, 'rscripts', '%s.rscript' % jobguid)

    def _getScriptResultPath(self, jobguid):
        return q.system.fs.joinPaths(q.dirs.tmpDir, 'rscripts', '%s.result' % jobguid)

    def _checkProgress(self):
        for pid in self._processManager.listRunningProcesses():
            retpid, proc_error_code = os.waitpid(pid, os.WNOHANG)
            if proc_error_code != None and retpid == pid:
                (agentcontrollerguid, jobguid) = self._processManager.getJob(pid)

                errorOutput = None

                result_path = self._getScriptResultPath(jobguid)
                error_path  = result_path.replace('.result', '.error')

                if not q.system.fs.exists(result_path) or proc_error_code != 0:
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

                if errorOutput != None:
                    self.scriptDiedCallback and self.scriptDiedCallback(agentcontrollerguid, jobguid, proc_error_code, errorOutput)

                self._processManager.processStopped(pid)
                reactor.callLater(2, self._processManager.removeProcess, pid) #Keep it alive for 2 seconds in case logging comes late.

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

    def addProcess(self, pid, fromm, jobguid):
        self.__runningProcesses.append(pid)
        procInfo = (pid, fromm, jobguid)
        self.__pidMapping[pid] = procInfo
        self.__jobMapping[self.__getJobId(fromm, jobguid)] = procInfo

    def processStopped(self, pid):
        '''
        The process has stopped: remove it from the process list, but keep the mapping (in case a log comes in late).
        '''
        self.__runningProcesses.remove(pid)

    def removeProcess(self, pid):
        '''
        Remove the process completely: remove the mapping.
        '''
        procInfo = self.__pidMapping.pop(pid)
        self.__jobMapping.pop(self.__getJobId(procInfo[1], procInfo[2]))

    def listRunningProcesses(self):
        return self.__runningProcesses

    def hasJob(self, fromm, jobguid):
        return self.__getJobId(fromm, jobguid) in self.__jobMapping

    def getProcess(self, fromm, jobguid):
        return self.__jobMapping.get(self.__getJobId(fromm, jobguid))[0]

    def getJob(self, pid):
        if self.__pidMapping.get(pid) != None:
            return self.__pidMapping.get(pid)[1:]
        else:
            return None

    def __getJobId(self, fromm, jobguid):
        return fromm + '@' + jobguid
