from  pymonkey import q
from collections import defaultdict
import cStringIO
from functools import partial


END_OF_COMMAND = "!"

class TaskletEngineFactory(object):
    def __init__(self):
    
        self.COMMANDS = dict() 
#        {'agent':_handleAgent, 
#        'shellcmd':_handleShellCmd, 
#        'qshellcmd':_handleQShellCmd, 
#        'qpackages':_handleQpackages, 
#        'portforward':_handlePortForward, 
#        'system':_handleSystem, 
#        'process':_Process}    
        
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
        self._history = defaultdict(cStringIO.StringIO) # will contain the accumulated commands for certain user
        self.taskletEngineFactory = taskletEngineFactory
        
        
    def execute(self, fromm, command, tasknr=None):
        # here're the commands parsing
        result = dict()
        try:
            command = command.strip() 
            
            
            if command == END_OF_COMMAND: # now we are ready to execute the accumulated command for this user
                commandInput = self._history[(fromm,tasknr)]
                # reset the history for this command
                self._history[(fromm,tasknr)] = cStringIO.StringIO()
                result =  self._executeMultipleLineCommand(fromm, tasknr, commandInput)
            else:
                # append this command to user's accumulated command
                self._history[(fromm,tasknr)].writelines("%s\n"%command);
                
        except Exception, ex:
            q.logger.log(ex)
            raise ex
        finally:
            return result
                
            
            
    
    def _executeMultipleLineCommand(self, fromm, tasknr, commandInput):
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
        
        
        args, options= self._getArgumentsAndOptions(commandInput)
          
        params = dict()
        
        params['cmd'] = command
        params['subcmd'] = commandLine[0] if commandLine else ''
        params['params'] = args
        params['options'] = options
        params['tasknr'] = tasknr
        params['from'] = fromm
        
        self.taskletEngineFactory.COMMANDS[command](params)
        return params
        
        
    def _getArgumentsAndOptions(self, commandInput): 
        args = commandInput.read().split("$")
        args = [x[:-1] for x in args]
        options = filter(lambda a: a[:1] =='-' , args)
        argsResult = args
        for arg in args:
            if arg in options:
                argsResult.remove(arg)            
            
        #args = list(set(args).difference(set(options)))                
        return argsResult, options
    
#    def _handleAgent(self, fromm, tasknr, commandLine, commandInput):
#        """
#        subcommands can be: register or passwd
#        """            
#        subCommand = commandLine.pop(0)
#        args = self._getArguments(commandLine, commandInput, ',')
#        
#        result = dict()
#        if subCommand == "register":
#            result = self.agentRegister(args)
#        elif subCommand == "passwd":
#            result = self.agentPasswd(*args)
#        else:
#            raise RuntimeError("Unknown subCommand %s"%subCommand)
#        return result
#            
#
#    def _handleShellCmd(self, fromm, tasknr, commandLine, commandInput):
#        options = self._getOptions(commandLine)
#        commandLine = self._removeOptions(commandLine)
#        
#        args = self._getArguments(commandLine, commandInput)
#        
#                    
#        self.shellCmd(args, options)
#
#    def _handleQShellCmd(self, fromm, tasknr, commandLine, commandInput):
#
#        options = self._getOptions(commandLine)
#        commandLine = self._removeOptions(commandLine)
#
#        args = self._getArguments(commandLine, commandInput)
#        
#        self.qshellCmd(args, options)
#
#    def _handleQpackages(self, fromm, tasknr, commandLine, commandInput):
#        """
#        subcommands can be: update or setsource or emptycache or install
#        """ 
#        subCommand = commandLine.pop(0)
#        args = self._getArguments(commandLine, commandInput, ':')
#        
#        result = dict()
#        if subCommand == "update":
#            result = self.qpackagesUpdate()
#        elif subCommand == "setsource":
#            result = self.qpackagesSetSource(*args)
#        elif subCommand == "emptycache":
#            result = self.qpackagesEmptyCache()
#        elif subCommand == "install":
#            result = self.qpackagesInstall(*args)
#        else:
#            raise RuntimeError("Unknown subCommand %s"%subCommand)
#        return result
#
#    def _handlePortForward(self, fromm, tasknr, commandLine, commandInput):
#        options = self._getOptions(commandLine)
#        commandLine = self._removeOptions(commandLine)
#        
#        args = self._getArguments(commandLine, commandInput, ':')
#        
#        # $serverport:$localdestination:$portondestination $login:$passwd@$sshServerInPubDC
#        serverPort , localDestination, portDestination, login, password_sshServerInPubDC = args 
#        password , sshServerInPubDC = password_sshServerInPubDC.split('@')
#        
#        self.portforward(args, options, serverPort , localDestination, portDestination, login, password, sshServerInPubDC)        
#
#    def _handleSystem(self, fromm, tasknr, commandLine, commandInput):
#        """
#        subcommands can be: setpasswd or reboot
#        """
#        subCommand = commandLine.pop(0)
#        args = self._getArguments(commandLine, commandInput, ',')
#        
#        
#        
#        result = dict()
#        if subCommand == "setpasswd":
#            result = self.systemSetPassword(*args)
#        elif subCommand == "reboot":
#            result = self.systemReboot()
#        else:
#            raise RuntimeError("Unknown subCommand %s"%subCommand)
#        return result
#
#    
#    def _Process(self, fromm, tasknr, commandLine, commandInput):
#        # list or kill or hardkill
#        subCommand = commandLine.pop(0)
#        
#        result = dict()
#        if subCommand == "list":
#            result = self.processList()
#        if subCommand == "kill":
#            result = self.processKill(fromm, tasknr)
#        if subCommand == "hardkill":
#            result = self.processHardKill(fromm, tasknr)
#        else:
#            raise RuntimeError("Unknown subCommand %s"%subCommand)
#        return result
#    
            
            
#    def agentRegister(self, xmppServerList):
#        print "agentRegister() xmppServerList:", xmppServerList
#        pass
#    
#    def agentPasswd(self, newPassword):
#        print "agentPasswd() newPasword:", newPassword
#
#    def shellCmd(self, args, options):
#        print "shellCmd() options: %s args: %s"% (options, args)
#    def qshellCmd(self, args, options):
#        print "qshellCmd() options: %s args: %s"% (options, args)
#    
#    def qpackagesUpdate(self):
#        print "qpackageUpdate()"
#        
#    def qpackagesSetSource(self, source):
#        print "qpackageSetSource() source:", source
#        
#    def qpackagesEmptyCache(self):
#        print "qpackagesEmptyCach()"
#        
#    def qpackagesInstall(self, name, version, domain):
#        print "qpackageInstall() name:%s version:%s domain:%s"% (name, version, domain)
#    
#    def portforward(self, options, serverPort , localDestination, portDestination, login, password, sshServerInPubDC):
#        print "portforward() options:%s serverPort:%s localDestination:%s portDestination:%s login:%s password:%s sshServerInPubDC:%s"% (options, serverPort , localDestination, portDestination, login, password, sshServerInPubDC)
#            
#    def systemSetPassword(self, username, password):
#        print "systemSetPassword() username:%s password:%s"% (username, password)
#    
#    def systemReboot(self):
#        print "systemReboot()"
#    
#    def processList(self):
#        print "processList()"
#        
#    def processKill(self, fromm, tasknr):
#        print "processKill() fromm:%s tasknr:%s"% (fromm, tasknr)
#        
#    def processHardKill(self, fromm, tasknr):
#        print "processHardKill() fromm:%s tasknr:%s" % (fromm, tasknr)
            
            
        