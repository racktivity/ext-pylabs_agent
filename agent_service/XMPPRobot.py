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

    
    def __init__(self, taskletEngineFactory):
        self._tasknr = 0
        self._history = defaultdict(cStringIO.StringIO) # will contain the accumulated commands for certain user
        self.taskletEngineFactory = taskletEngineFactory
        
        
    def execute(self, fromm, command):
        # command parsing
        q.logger.log("==========> received:%s , from:%s"%(command, fromm))
        try:
            if command == END_OF_COMMAND: # now we are ready to execute the accumulated command for this user
                commandInput = self._history[fromm]
                # reset the history for this command
                self._history[fromm] = cStringIO.StringIO()
                self._executeMultipleLineCommand(fromm, commandInput)
                result = self._tasknr
                self._tasknr += 1
                                                
                return result
            else:
                if fromm not in self._history:
                    if not command.startswith('!'):#we are waiting for a start of commands, and rubbish is received
                        q.logger.log('received invalid message %s while waiting for a new command'%command)                        
                        
                # append this command to user's accumulated command
                self._history[fromm].writelines("%s\n"%command);
                
        except Exception, ex:
            q.logger.log(ex)
            raise ex
            self._history[fromm] = cStringIO.StringIO()
        finally:
            return None
                
            
            
    
    def _executeMultipleLineCommand(self, fromm, commandInput):
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
        
        if command not in self.taskletEngineFactory.COMMANDS:
            raise RuntimeError("Illegal command %s used"% command)
        
        
        args, options= CommandExecuter._getArgumentsAndOptions(commandInput)
          
        params = dict()
        
        params['cmd'] = command
        params['subcmd'] = commandLine[0] if commandLine else ''
        params['params'] = args
        params['options'] = options
        params['tasknr'] = self._tasknr
        params['from'] = fromm
        
        self.taskletEngineFactory.COMMANDS[command](params)
        
        # return the output of execution
        
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
        