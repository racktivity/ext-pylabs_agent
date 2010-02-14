'''
PyLabs XMPP client module
'''
from pymonkey import q, i
#from distutils.cmd import Command
import xmpp, select
from threading import Thread
from collections import defaultdict

BEGIN_COMMAND = '!'
END_COMMAND = '!'
BEGIN_LOG = '@'
BEGIN_RESULT = '!!!'
END_RESULT = '!!!'
BEGIN_TASKNR = '<ID>'

TYPE_RESULT = 'RESULT'
TYPE_LOG = 'LOG'
TYPE_COMMAND = 'COMMAND'
TYPE_ERROR = 'ERROR'
TYPE_TASKNUMBER = 'TASKNUMBER'
TYPE_UNKNOWN = 'UNKNOWN'

class XMPPClient(object):
    '''
    classdocs
    '''
    def __init__(self, jid, password, port=5222,resource=None):
        '''
        Constructor
        @param jid:                  XMPP JID
        @type jid:                   string

        @param password:             Password
        @type password:              string

        @param resource:             Resource name
        @type resource:              string
        '''        
        
        self.userJID = jid
        self.username = xmpp.JID(self.userJID).getNode()
        self.domain = xmpp.JID(self.userJID).getDomain()
        self.userpassword = password        
        self._resultMessage = ''
        self.status = 'NOT_CONNECTED'
        self.callbacks = {TYPE_COMMAND:None, TYPE_LOG:None, TYPE_RESULT:None, TYPE_ERROR:None, TYPE_TASKNUMBER:None, TYPE_UNKNOWN:None}
        self.port = port
        self._client = xmpp.Client(xmpp.JID(self.userJID).getDomain(), port = self.port, debug = [])
     
    def connect(self, server=None):
        """
        Connects the client to xmpp server with the credentials specified

        @param server:               If specified, connect to a specific server hosting the domain 
        @type server:                string

        @return:                     True in case of successful connection
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """        
        if self.status <> 'NOT_CONNECTED':
            raise RuntimeError('The XmppClient has already been started.')        
        self.server = server
        q.logger.log("[XMPPCLIENT] Starting the xmpp client to " + self.username + "@" + self.server, 5)
        return self._connect()
    
    def _connect(self):
        self.status = 'CONNECTING'        
        q.logger.log("[XMPPCLIENT] Connecting to server %s with xmpp user %s'" % (self.server, self.username) )        
        self._client.connect((self.server, self.port))
        if not self._client.connected:
            q.logger.log('[XMPPCLIENT] Failed to connect to server:%s, port:%s'%(self.server, self.port))
            return False
        if self._client.auth(xmpp.JID(self.userJID).getNode(), self.userpassword):
            #authenticated
            self.status = 'RUNNING'
            q.logger.log("[XMPPCLIENT] Server '" + self.server + "' authenticated user '" + self.username + "'", 5)
            self.sendPresence()
        else:
            q.logger.log('[XMPPCLIENT] Failed to authenticate user %s with server %s'%(self.userJID, self.server))
            return False
            
        #Now it's connected
        self.status = 'CONNECTED'
        self._client.RegisterHandler('message', self._message_Recieved)
        self._client.RegisterHandler('presence', self._presence_received)
        q.logger.log("[XMPPCLIENT] _connected:  Connected to server [%s], trying with usersname [%s]" % (self.server, self.username))
        q.logger.log("DEBUG: CLIENT STATUS: %s"% self._client.isConnected())        
        
        self._doConnect()
        
        return True

    def _doConnect(self):
        
        def _listen(client):
            q.logger.log('DEBUG: STARTING LISTENER')
            running = 1
            socketlist = {client.Connection._sock:'xmpp'}
            while running:            
                (i , o, e) = select.select(socketlist.keys(),[],[],1)
                for each in i:
                    if socketlist[each] == 'xmpp':
                        q.logger.log('DEBUG: CALLING PROCESS.......................')
                        client.Process(1)                    
                    else:
                        q.logger.log("Unknown socket type: %s" % repr(socketlist[each]))

        t = Thread(target=_listen, args=(self._client,))
        #t = Thread(target=self._listen)
        t.start()
        
    def _presence_received(self, conn, message):
        type_ = message.getType()
        fromm = message.getFrom().getStripped() or ''
            
        q.logger.log("[XMPPCLIENT] Presence received from '" + fromm + "' of type '" + type_ +"'", 5)
        
    def _message_Recieved(self, conn, message):
        q.logger.log("DEBUG: MESSAGE RECEIVED ............")
        sender = message.getFrom().getStripped()                
        receiver = message.getTo().getStripped()
        messageid = message.getID()
        message = message.getBody()
        
        q.logger.log('[XMPPCLIENT] Message is received, from:%s, to:%s, id:%s, body:%s'%(sender, receiver, messageid, message)) 
        
        messageHanlder = XMPPMessageHandler()
        messageObject = messageHanlder.deserialize(sender, receiver, messageid, message)
        
        callback = self.callbacks[messageObject.type_]
        if callback:
            callback(messageObject)
        else:
            q.logger.log("[XMPPCLIENT] Warning, no callback is registered for type:%s"%messageObject.type_)
            
            
    def disconnect(self):
        """
        Disconnects the client to xmpp server with the credentials specified

        @return:                     True in case disconnecting succeeded
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        if self.status == 'NOT_CONNECTED':
            return False
        
        q.logger.log("[XMPPCLIENT] Stopping the xmpp client to " + self.username + "@" + self.server, 5)
        self._client.disconnect()
        return True

    def sendPresence(self, to=None, type_=None):
        ''' Send a presence
        @param to: The username of the client to send the presence to. None=send to all your friends
        @type to: string
        @param type: The type of the presence. Possible values: None=available, unavailable, subscribe, subscribed 
        @type type: string
        '''
        if self.status <> 'RUNNING' and self.status <> 'CONNECTED':
            raise RuntimeError("NOT connected client")
        
        q.logger.log("[XMPPCLIENT] Sending presence of type '" + str(type_) +"' to " + str(to) + "'", 5)
        self._client.send(xmpp.Presence(to = to, typ = type_))
        
    def sendMessage(self, xmppmessage):
        """
        @param xmppmessage           XMPP message
        @type xmppmessage            XMPPMessage

        @return:                     Unique identifier for this message
        @rtype:                      string

        @raise e:                    In case an error occurred, exception is raised
        """        
        
        if self.status <> 'RUNNING' and self.status <> 'CONNECTED':
            raise RuntimeError("NOT connected client")
        
        sender = xmppmessage.sender
        receiver = xmppmessage.receiver 
        
        q.logger.log("[XMPPCLIENT] Sending message [%s] from:%s to:%s'"%(str(xmppmessage), sender, receiver),5)            
        return self._client.send(xmpp.Message(to = receiver, body = str(xmppmessage), typ = 'chat'))
    
    
    def setCommandReceivedCallback(self, commandHandler):
        """
        @param commandHandler:           Callable which is called whenever a command message is received.
        @type commandHandler:            callable
        @note:                       Interface for the callable must be (XMPPCommandMessage)
        """
        self.callbacks[TYPE_COMMAND] = commandHandler

    def setLogReceivedCallback(self, logHandler):
        """
        @param logHandler:           Callable which is called whenever a log message is received.
        @type logHandler:            callable
        @note:                       Interface for the callable must be (XMPPLogMessage)
        """
        self.callbacks[TYPE_LOG] = logHandler

    def setErrorReceivedCallback(self, errorHandler):
        """
        @param errorHandler:         Callable which is called whenever a error message is received.
        @type errorHandler:          callable
        @note:                       Interface for the callable must be (XMPPErrorMessage)
        
        """
        self.callbacks[TYPE_ERROR] = errorHandler

    def setResultReceivedCallback(self, resultHandler):
        """
        @param resultHandler:        Callable which is called whenever a result message is received.
        @type resultHandler:         callable
        @note:                       Interface for the callable must be (XMPPResultMessage)
        """
        self.callbacks[TYPE_RESULT] = resultHandler

    def setMessageReceivedCallback(self, messageHandler):
        """
        @param messageHandler:       Callable which is called whenever a message is received.
        @type messageHandler:        callable
        @note:                       Interface for the callable must be (XMPPMessage)
        """
        self.callbacks[TYPE_UNKNOWN] = messageHandler
        


class XMPPMessageHandler(object):
    
    
    
    def __init__(self):
        pass
    
    def serialize(self, xmppmessage):
        """
        Serializes the XMPPMessage object to PyLabs XMPP message format
        
        @param command:              String containing command to execute e.g. 'machine start'
        @type command:               string
        @param params:               List of strings which are input parameters for the specified command e.g. ['mymachine']
        
        @return:                     String containing command in PyLabs XMPP message format
        @rtype:                      string
        @note:                       Example !machine start
        @note:                                mymachine
        @note:                               !
        """        
        
        return str(xmppmessage)
        
    def deserialize(self, sender, receiver, messageid, message):
        """
        Deserializes a PyLabs XMPP command message to a XMPPMessage object
        
        @param message:              String containing command in PyLabs XMPP message format
        @type message:               string
        
        @return:                     XMPPMessage object
        @rtype:                      XMPPMessage
        """
        
        message = message.strip()
        
        if message.startswith(BEGIN_RESULT): # we must check on result before checking on command prefix
            index = message.find('\n')            
            tasknumber, returncode = message[len(BEGIN_RESULT):index].split()
            returnvalue = message[index+1:-len(END_RESULT)]
            resultMessage = XMPPResultMessage(sender, receiver, messageid, tasknumber, returncode, returnvalue)
            return resultMessage
        
        elif message.startswith(BEGIN_COMMAND):# !<command> [subcommand]\n[params]*\n!
            index = message.find('\n')                     
            commandLine = message[:index].split()
            command = commandLine.pop(0)
            subcommand = commandLine[0] if commandLine else ''            
            args, options= self._getArgumentsAndOptions('\n'.join(message[index+1:]))
            commandMessage = XMPPCommandMessage(sender, receiver, messageid, command, subcommand, {'params':args, 'options':options})            
            return commandMessage
            
        elif message.startswith(BEGIN_LOG): # @<tasknr>|<logentry>            
            index = message.find('|')
            tasknumber = message[1:index]
            logentry = message[index+1:]
            logMessage = XMPPLogMessage(sender, receiver, messageid, tasknumber, logentry)
            return logMessage
        
        elif message.startswith(BEGIN_TASKNR):# <ID>Tasknumber          
            tasknumber = message[len(BEGIN_TASKNR):]
            tasknumberMessage = XMPPTaskNumberMessage(sender, receiver, messageid, tasknumber)
            return tasknumberMessage        
        
    
    def _getArgumentsAndOptions(self, commandInput): 
        args = commandInput.split("$")
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
    
class XMPPMessage(object):
    """
    Class representing a generic PyLabs XMPP message
    """
    def __init__(self, sender, receiver, message, messageid=None):
        pass

class XMPPCommandMessage(object):
    """
    Class representing a PyLabs XMPP command message
    """
    type_ = TYPE_COMMAND    
    def __init__(self, sender, receiver, messageid, command, subcommand='', params=None):
        self.sender = sender
        self.reciver = receiver
        self.messageid = messageid
        self.command = command
        self.subcommand = subcommand
        self.params = params
        
    def __str__(self):        
        params = self.params['params'] + self.params['options']        
        return '%(begin)s%(command)s %(subcommand)s\n%(params)s\n%(end)s'%{'begin':BEGIN_COMMAND, 'end':END_COMMAND, 'command':self.command, 'subcommand':self.subcommand, 'params':'\n$'.join(params)}        


class XMPPResultMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP result message
    """
    type_ = TYPE_RESULT
    def __init__(self, sender, receiver, messageid, tasknumber, returncode, returnvalue):
        
        self.sender = sender
        self.receiver = receiver
        self.messageid = messageid
        self.tasknumber = tasknumber
        self.returncode = returncode
        self.returnvalue = returnvalue
        

    def __str__(self):
        return '%(begin)s%(tasknumber)s %(returncode)s\n%(returnvalue)s\n%(end)s'%{'begin':BEGIN_RESULT, 'end':END_RESULT, 'tasknumber':self.tasknumber, 'returncode':self.returncode, 'returnvalue':self.returnvalue}


class XMPPLogMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP log message
    """
    type_ = TYPE_LOG
    def __init__(self, sender, receiver, messageid, tasknumber, logentry):
        self.sender = sender
        self.receiver = receiver
        self.messageid = messageid
        self.tasknumber = tasknumber
        self.logentry = logentry
        
    def __str__(self):
        return '@%s|%s'%(self.tasknumber, self.logentry)


class XMPPErrorMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP error message
    """
    type_ = TYPE_ERROR
    def __init__(self, sender, receiver, messageid, tasknumber, returncode, returnvalue):
        pass

class XMPPTaskNumberMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP error message
    """
    type_ = TYPE_TASKNUMBER
    def __init__(self, sender, receiver, messageid, tasknumber):
        self.sender = sender
        self.receiver = receiver
        self.messageid = messageid
        self.tasknumber = tasknumber
    
    def __str__(self):
        return '%(begin)s%(tasknumber)s'%{'begin':BEGIN_TASKNR, 'tasknumber':self.tasknumber}
    