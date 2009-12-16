
from collections import defaultdict

WAITING = "waiting"
PENDING = "pending"
END_OF_COMMAND = "!"

class CommandExecuter(object):
    COMMANDS = {'agent':CommandExecuter._handleAgent, 
            'shellcmd':CommandExecuter._handleShellCmd, 
            'qshellcmd':CommandExecuter._handleQShellCmd, 
            'qpackages':CommandExecuter._handleQpackages, 
            'portforward':CommandExecuter._handlePortForward, 
            'system':CommandExecuter._handleSystem, 
            'process':CommandExecuter._Process}

    
    def __init__(self):
        self._history = defaultdict(list) # will contain the accumulated commands for certain user
        
    def execute(self, fromm, command, jobID=None):
        # here're the commands parsing
        command = command.strip() 
        
        # append this command to user's accumulated command
        self._history[(fromm,jobID)].extend(command.split('\n'))
        if command == END_OF_COMMAND: # now we are ready to execute the accumulated command for this user
            commandInput = self._history[(fromm,jobID)]
            # reset the history for this command
            self._history[(fromm,jobID)] = list()
            self._executeMultipleLineCommand(fromm, jobID, commandInput)
            
            
    
    def _executeMultipleLineCommand(self, fromm, jobID, commandInput):
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
        commandLine = commandInput.pop(0).replace('!','',1).split()
        
        command = commandLine.pop(0)
        
        
        if command not in COMMANDS:
            raise RuntimeError("Illegal command %s used"% command)
        
        COMMANDS[command](fromm, jobID, commandLine, commandInput)
        
        
    def _getArguments(self, commandInput, seperator=None): 
        args = list()
        for command in commandInput:    
            
            if command == END_OF_COMMAND:
                break
                        
            if seperator:
                args.extend(command.split(seperator))
            else:
                args.append(command)
        return args
    
    def _removeOptions(self, commandLine):
        args = list()
        for element in commandLine:
            if not element.start('-'):
                args.append(element[1:]) # add the option without '-'
        return args
    
    def _getOptions(self, commandLine):        
        options = list()
        for element in commandLine:
            if element.start('-'):
                options.append(element[1:]) # add the option without '-'
        return options
      
    @classmethod
    def _handleAgent(cls, fromm, jobID, commandLine, commandInput):
        """
        subcommands can be: register or passwd
        """            
        subCommand = commandLine[0]
        args = list()
        args.extend(commandLine[1:])
        args.extend(self._getArguments(commandInput, ','))
        
        if subCommand == "register":
            self.agentRegister(*args)
        if subCommand == "passwd":
            self.agentPasswd(*args)

    @classmethod
    def _handleShellCmd(cls, fromm, jobID, commandLine, commandInput):
        options = self._getOptions(commandLine)
        commandLine = self._removeOptions(commandLine)
        
        args = list()
        args.extend(commandLine)
        args = self._getArguments(commandInput, ',')
        
                    
        self.shellCmd(args, options)

    @classmethod
    def _handleQShellCmd(cls, fromm, jobID, commandLine, commandInput):

        options = self._getOptions(commandLine)
        commandLine = self._removeOptions(commandLine)

        args = list()
        args.extend(commandLine)
        args = self._getArguments(commandInput, ',')
        
        self.qshellCmd(args, options)

    @classmethod
    def _handleQpackages(cls, fromm, jobID, commandLine, commandInput):
        """
        subcommands can be: update or setsource or emptycache or install
        """ 
        subCommand = commandLine[0]
        args = list()
        args.extend(commandLine[1:])
        args = self._getArguments(commandInput, ':')
        
        
        if subCommand == "update":
            self.qpackagesUpdate()
        if subCommand == "setsource":
            self.qpackagesSetSource(*args)
        if subCommand == "emptycache":
            self.qpackagesEmptyCache()
        if subCommand == "install":
            self.qpackagesInstall(*args)

    @classmethod
    def _handlePortForward(cls, fromm, jobID, commandLine, commandInput):
        args = list()
        options = self._getOptions(commandLine)
        commandLine = self._removeOptions(commandLine)
        
        
        for element in commandLine:
            args.extend(elements.split(':'))        
        args = self._getArguments(commandInput, ':')
        
        # $serverport:$localdestination:$portondestination $login:$passwd@$sshServerInPubDC
        serverPort , localDestination, portDestination, login, password_sshServerInPubDC = args 
        password , sshServerInPubDC = password_sshServerInPubDC.split('@')
        
        self.portforward(args, options, serverPort , localDestination, portDestination, login, password, sshServerInPubDC)        

    @classmethod
    def _handleSystem(cls, fromm, jobID, commandLine, commandInput):
        """
        subcommands can be: setpasswd or reboot
        """
        args = list()
        args.extend(commandLine[1:])
        args = self._getArguments(commandInput, ',')
        
        subCommand = commandLine[0]
        
        if subCommand == "setpasswd":
            self.systemSetPassword(*args)
        if subCommand == "reboot":
            self.systemReboot()

    @classmethod
    def _Process(cls, fromm, jobID, commandLine, commandInput):
        # list or kill or hardkill
        subCommand = commandLine[0]
        
        if subCommand == "list":
            self.processList()
        if subCommand == "kill":
            self.processKill(fromm, jobID)
        if subCommand == "hardkill":
            self.processHardKill(fromm, jobID)
            
            
    def agentRegister(self, xmppServerList):
        print "agentRegister() xmppServerList:", xmppServerList
        pass
    
    def agentPasswd(self, newPassword):
        print "agentPasswd() newPasword:", newPassword

    def shellCmd(self, args, options):
        print "shellCmd() options: %s args: %s"% (options, args)
    def qshellCmd(self, args, options):
        print "qshellCmd() options: %s args: %s"% (options, args)
    
    def qpackagesUpdate(self):
        print "qpackageUpdate()"
        
    def qpackagesSetSource(self, source):
        print "qpackageSetSource() source:", source
        
    def qpackagesEmptyCache(self):
        print "qpackagesEmptyCach()"
        
    def qpackagesInstall(self, name, version, domain):
        print "qpackageInstall() name:%s version:%s domain:%s"% (name, version, domain)
    
    def portforward(self, options, serverPort , localDestination, portDestination, login, password, sshServerInPubDC):
        print "portforward() options:%s serverPort:%s localDestination:%s portDestination:%s login:%s password:%s sshServerInPubDC:%s"% (options, serverPort , localDestination, portDestination, login, password, sshServerInPubDC)
            
    def systemSetPassword(self, username, password):
        print "systemSetPassword() username:%s password:%s"% (username, password)
    def systemReboot(self):
        print "systemReboot()"
    
    def processList(self):
        print "processList()"
        
    def processKill(self, fromm, jobID):
        print "processKill() fromm:%s jobID:%s"% (fromm, jobID)
        
    def processHardKill(self, fromm, jobID):
        print "processHardKill() fromm:%s jobID:%s" % (fromm, jobID)
            
                        
        
            
            
        