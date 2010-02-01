from  pymonkey import q
from collections import defaultdict
import cStringIO
from functools import partial
import uuid

END_OF_COMMAND = "!"

class TaskletEngineFactory(object):
    def __init__(self):
    
        self.COMMANDS = dict() 
        
        q.system.fswalker.walk(q.system.fs.joinPaths(q.dirs.appDir, "agent", "cmds"), callback=self.processCommandDir, arg=self.COMMANDS, includeFolders=True, recursive=False)
    
    def processCommandDir(self, arg, path):
        if not q.system.fs.isDir(path):
            return
        taskletEngine = q.getTaskletEngine(path)
        arg[q.system.fs.getBaseName(path)] = partial(self.executeTasklets, taskletEngine)
    
    def executeTasklets(self, taskletEngine, params):
        print params
        taskletEngine.execute(params,tags=(params['cmd'],))    

        

class CommandExecuter(object):

    
    def __init__(self, taskletEngineFactory, xmppClients=None, scriptExecuter=None):
        self._tasknr = 0
        self._tasknrToJID = dict()
        self._history = defaultdict(cStringIO.StringIO) # will contain the accumulated commands for certain user
        self._taskletEngineFactory = taskletEngineFactory
        self._xmppClients = xmppClients
        self._scriptExecuter = scriptExecuter
        self._scriptExecuter.setScriptDoneCallback(self._qshellCommandDone)
        self._scriptExecuter.setScriptDiedCallback(self._qshellCommandDied)
        
        
    def execute(self, fromm, command, id, xmppServer):
        # command parsing
        try:
            if command == END_OF_COMMAND: # now we are ready to execute the accumulated command for this user                
                commandInput = self._history[(fromm, xmppServer)]                
                self._executeMultipleLineCommand(fromm, commandInput, id, xmppServer)                
            else:
                if (fromm, xmppServer) not in self._history:
                    if not command.startswith('!'):#we are waiting for a start of commands, and rubbish is received
                        q.logger.log('received invalid message %s while waiting for a new command'%command)                        
                    elif command.endswith('\n%s'%END_OF_COMMAND): # full command
                        fullCommand = cStringIO.StringIO()
                        fullCommand.writelines("%s\n"%command[:-2])
                        self._executeMultipleLineCommand(fromm, fullCommand, id, xmppServer)
                    else:
                        # append this command to user's accumulated command
                        self._history[(fromm, xmppServer)].writelines("%s\n"%command);
                else:
                    # append this command to user's accumulated command
                    self._history[(fromm, xmppServer)].writelines("%s\n"%command);
                
        except Exception, ex:
            q.logger.log(ex)            
            # reset the history for this command
            if (fromm, xmppServer) in self._history:
                del self._history[(fromm, xmppServer)]
            raise ex
        finally:
            return None
                
            
            
    
    def _executeMultipleLineCommand(self, fromm, commandInput, id, xmppServer):
        """
        we will execute the lines of each command
        e.g 
           !perm set 
           *@superadmin.eur.daas.com,*@cloud1.ghent.goodguys.com 
           all:1        
           !
        """
        if not commandInput:
            return # nothing to execute
        
        # first line will contain the command name
        commandInput.seek(0)
        commandLine = commandInput.readline().replace('!','',1).split()
        
        
        command = commandLine.pop(0)        
        
        if command not in self._taskletEngineFactory.COMMANDS:
            raise RuntimeError("Illegal command %s used"% command)
        
        
        args, options= CommandExecuter._getArgumentsAndOptions(commandInput)
        
        tasknr = self._generateTasknr(fromm, xmppServer)
        if self._xmppClients[xmppServer]:
            self._xmppClients[xmppServer].sendMessage(fromm, 'chat', id, tasknr)
          
        params = dict()
        
        params['cmd'] = command
        params['subcmd'] = commandLine[0] if commandLine else ''
        params['params'] = args
        params['options'] = options
        params['tasknr'] = tasknr
        params['from'] = fromm
        params['executeAsyncQshellCommand'] = partial(self._executeAsyncQshellCommand, fromm, tasknr)
        params['executeAsyncShellCommand'] = partial(self._executeAsyncShellCommand, fromm, tasknr)
        params['killTask'] = partial(self._killTask, fromm)
        params['stopTask'] = partial(self._stopTask, fromm)
        
        
        # the following call should be async
        self._taskletEngineFactory.COMMANDS[command](params)
        
        # check whehter this tasklet finishes its work
        if 'returncode' in params:
            self._commandExecuted(params, id)             
        

    def _executeAsyncQshellCommand(self, fromm, tasknr, script, params, captureOutput=True, maxLogLevel=5):
        if 'executeAsyncQshellCommand' in params:
            del params['executeAsyncQshellCommand']
        if 'executeAsyncShellCommand' in params:
            del params['executeAsyncShellCommand']
        if 'killTask' in params:
            del params['killTask']
        if 'stopTask' in params:
            del params['stopTask']
        self._scriptExecuter.executeQshellCommand(fromm, tasknr, params, script, captureOutput=captureOutput, maxLogLevel=maxLogLevel)
        
        
    def _executeAsyncShellCommand(self, fromm, tasknr, script, params, captureOutput=True):        
        self._scriptExecuter.executeShellCommand(fromm, tasknr, params, script, captureOutput)
    
    def _stopTask(self, fromm, tasknr):
        return self._scriptExecuter.stop(fromm, tasknr)
    
    def _killTask(self, fromm, tasknr):
        return self._scriptExecuter.kill(fromm, tasknr)
        
    def _qshellCommandDone(self, fromm, tasknr, params):
        q.logger.log('_qshellCommandDone Command Done from:%s, tasknr:%s, params:%s'%(fromm, tasknr, params), 6)        
        params['tasknr'] = tasknr
        self._commandExecuted(params, self.generateXMPPMessageID())
        
    def _qshellCommandDied(self, fromm, tasknr, errorcode, erroroutput):
        q.logger.log('_qshellCommandDied Command Died from:%s, tasknr:%s, errorcode:%s, erroroutput:%s'%(fromm, tasknr, errorcode, erroroutput), 6)
        params = dict()        
        params['returnmessage'] = erroroutput
        params['returncode'] = errorcode
        params['tasknr'] = tasknr
        self._commandExecuted(params, self.generateXMPPMessageID())
        
        
    def _commandExecuted(self, params, id):
        returnmessage = "!!!%(tasknr)s %(returncode)s%(returnmessage)s\n!!!"% \
        {'tasknr':params['tasknr'], 'returncode':params['returncode'], \
         'returnmessage': '\n%s'%params['returnmessage'] if params['returnmessage'] else ''}
        q.logger.log('_commandExecuted params:%s, id:%s, returnmessage:%s'%(params, id, returnmessage), 6)        
        fromm, xmppServer = self._tasknrToJID[params['tasknr']]       
        if self._xmppClients[xmppServer]:
            q.logger.log('sending %s to %s'%(returnmessage, fromm), 6)
            self._xmppClients[xmppServer].sendMessage(fromm, 'chat', id, returnmessage)
        
        if params['tasknr'] in self._tasknrToJID:
            del self._tasknrToJID[params['tasknr']]
    
        # reset the history for this command
        if (fromm, xmppServer) in self._history:
            del self._history[(fromm, xmppServer)]        
        
    # return the output of execution
    def _generateTasknr(self, fromm, xmppServer,jobID=None):
        self._tasknr += 1
        tasknr = str(self._tasknr)  
        self._tasknrToJID[tasknr] = (fromm, xmppServer)     
        return tasknr
    
    def getJIDFromTasknr(self, tasknr):
        return self._tasknrToJID[tasknr][0]
    
    def getXmppServerFromTasknr(self, tasknr):
        return self._tasknrToJID[tasknr][1]
    
    def getTaskNrs(self):
        return self._tasknrToJID.keys()
    
    def generateXMPPMessageID(self):
        return str(uuid.uuid1())
        
    @classmethod
    def _getArgumentsAndOptions(cls, commandInput): 
        args = commandInput.read().split("$")
        argsResult = list()
        options = list()
        def mod(arg):
            arg = arg[:-1]
            if arg[:1] == '-':
                options.append(arg)                
            else:
                argsResult.append(arg)                
        
        filter(mod, args)
        return argsResult, options
        