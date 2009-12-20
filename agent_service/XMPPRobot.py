from  pymonkey import q
from collections import defaultdict
import cStringIO
from functools import partial


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

    
    def __init__(self, taskletEngineFactory, xmppClient=None):
        self._tasknr = 0
        self.tasknrToJID = dict()
        self._history = defaultdict(cStringIO.StringIO) # will contain the accumulated commands for certain user
        self._taskletEngineFactory = taskletEngineFactory
        self._xmppClient = xmppClient
        
        
    def execute(self, fromm, command, id):
        # command parsing
        q.logger.log("DEBUG: execute(fromm:%s, command:%s, id:%s)"%(fromm, command, id))
        try:
            if command == END_OF_COMMAND: # now we are ready to execute the accumulated command for this user                
                commandInput = self._history[fromm]                
                self._executeMultipleLineCommand(fromm, commandInput, id)                
            else:
                if fromm not in self._history:
                    if not command.startswith('!'):#we are waiting for a start of commands, and rubbish is received
                        q.logger.log('received invalid message %s while waiting for a new command'%command)                        
                    elif command.endswith('\n%s'%END_OF_COMMAND): # full command
                        fullCommand = cStringIO.StringIO()
                        fullCommand.writelines("%s\n"%command[:-2])
                        self._executeMultipleLineCommand(fromm, fullCommand, id)
                    else:
                        # append this command to user's accumulated command
                        q.logger.log('DEBUG: add %s to buffer from: %s'%(command, fromm))
                        self._history[fromm].writelines("%s\n"%command);
                else:
                    # append this command to user's accumulated command
                    q.logger.log('DEBUG: append %s to buffer from: %s'%(command, fromm))
                    self._history[fromm].writelines("%s\n"%command);
                
        except Exception, ex:
            q.logger.log(ex)            
            # reset the history for this command
            if fromm in self._history:
                del self._history[fromm]
            raise ex
        finally:
            return None
                
            
            
    
    def _executeMultipleLineCommand(self, fromm, commandInput, id):
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
        q.logger.log('DEBUG _executeMultipleLineCommand from:%s , commandInput:%s'%(fromm, commandInput.getvalue()))                                
        commandLine = commandInput.readline().replace('!','',1).split()
        
        
        command = commandLine.pop(0)        
        
        if command not in self._taskletEngineFactory.COMMANDS:
            raise RuntimeError("Illegal command %s used"% command)
        
        
        args, options= CommandExecuter._getArgumentsAndOptions(commandInput)
        
        tasknr = self._generateTasknr(fromm)
        if self._xmppClient:
            self._xmppClient.sendMessage(fromm, 'chat', id, str(tasknr))
          
        params = dict()
        
        params['cmd'] = command
        params['subcmd'] = commandLine[0] if commandLine else ''
        params['params'] = args
        params['options'] = options
        params['tasknr'] = tasknr
        params['from'] = fromm
        
        #the following call should be async
        self._taskletEngineFactory.COMMANDS[command](params)
        
        self._commandExecuted(params, id)
        

    def _commandExecuted(self, params, id):
        output = "!!!%(tasknr)s %(returncode)s \n%(returnmessage)s\n!!!"%{'tasknr':params['tasknr'], 'returncode':params['returncode'], 'returnmessage':params['returnmessage']}
        fromm = self.tasknrToJID[params['tasknr']]        
        if self._xmppClient:
            self._xmppClient.sendMessage(fromm, 'chat', id, output)
        
        if params['tasknr'] in self.tasknrToJID:
            del self.tasknrToJID[params['tasknr']]
    
        # reset the history for this command
        if fromm in self._history:
            del self._history[fromm]        
        
    # return the output of execution
    def _generateTasknr(self, fromm, jobID=None):
#        if jobID in self._jobIDToTasknr:
#            return self._jobIDToTasknr[jobID]
#        self._tasknr = self._tasknr + 1
#        self._jobIDToTasknr[jobID] = self._tasknr
        self._tasknr += 1  
        self.tasknrToJID[self._tasknr] = fromm     
        return self._tasknr
        
    @classmethod
    def _getArgumentsAndOptions(cls, commandInput): 
        args = commandInput.read().split("$")
        argsResult = list()
        def mod(arg):
            arg = arg[:-1]
            if arg[:1] == '-':
                return True
            else:
                argsResult.append(arg)
                return False
        
        options = filter(mod, args)
        return argsResult, options
        