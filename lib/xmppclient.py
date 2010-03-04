'''
INCUBAID BSD version 2.0 
Copyright (c) 2010 Incubaid BVBA

All rights reserved. 
 
Redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following 
conditions are met: 
 
* Redistributions of source code must retain the above copyright 
notice, this list of conditions and the following disclaimer. 

* Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in    the documentation and/or other materials provided with the   distribution. 
* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
 
THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
'''

from pymonkey import q, i
import xmpp, select
from threading import Thread
import sys, traceback

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
    NUMBER_OF_RETRIES = 3
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
        self.domain = xmpp.JID(self.userJID).getDomain()
        self.userpassword = password        
        self._resultMessage = ''
        self.status = 'NOT_CONNECTED'
        self.callbacks = {TYPE_COMMAND:None, TYPE_LOG:None, TYPE_RESULT:None, TYPE_ERROR:None, TYPE_TASKNUMBER:None, TYPE_UNKNOWN:None}
        self.port = port
        self._client = xmpp.Client(self.domain, port = self.port, debug = [])
     
    def connect(self, server):
        """
        Connects the client to xmpp server with the credentials specified

        @param server:               If specified, connect to a specific server hosting the domain 
        @type server:                string

        @return:                     True in case of successful connection
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """        
        if self.status == 'CONNECTED':
            q.logger.log("Client is already connected to %s"%(self.server)) 
            return True       
        self.server = server
        q.logger.log("Starting the xmpp client to %s at %s"%(self.userJID, self.server), 5)
        return self._connect()
    
    def _connect(self):
        self.status = 'CONNECTING'        
        q.logger.log("Connecting to server %s with xmpp user %s'" % (self.server, self.userJID) )
        tries = 0 
        
        result = self._client.connect((self.server, self.port))
        while tries < self.NUMBER_OF_RETRIES and not result:   
            result = self._client.connect((self.server, self.port))          
            tries +=1
            
        if not self._client.connected:
            q.logger.log('Failed to connect to server:%s, port:%s'%(self.server, self.port), 4)
            return False
        if self._client.auth(xmpp.JID(self.userJID).getNode(), self.userpassword):
            #authenticated
            self.status = 'RUNNING'
            q.logger.log("Server '%s' authenticated user '%s'"%(self.server, self.userJID), 3)
        else:
            q.logger.log('Failed to authenticate user %s with server %s'%(self.userJID, self.server), 4)
            return False
            
        #Now it's connected
        self.status = 'CONNECTED'
        self._client.sendInitPresence()
        self._client.RegisterHandler('message', self._messageRecieved)
        self._client.RegisterHandler('presence', self._presenceReceived)
        q.logger.log("Connected to server [%s], trying with usersname [%s]" % (self.server, self.userJID), 5)
        
        self._doConnect()
        
        return True

    def _doConnect(self):
        
        def _listen(client):
            socketlist = {client.Connection._sock:'xmpp'}
            while True:            
                (i , _, _) = select.select(socketlist.keys(),[],[],1)
                try:
                    for each in i:
                        if socketlist[each] == 'xmpp':                        
                            client.Process(1)                    
                        else:
                            q.logger.log("Unknown socket type: %s" % repr(socketlist[each]))
                except:
                    q.logger.log('Exception occurred while listening %s'%traceback.format_exception(*sys.exc_info()), 4)

        t = Thread(target=_listen, args=(self._client,))
        #t = Thread(target=self._listen)
        t.start()
        
    def _presenceReceived(self, conn, message):
        type_ = message.getType()
        fromm = message.getFrom().getStripped() or ''
            
        q.logger.log("Presence received from %s of type %s"%(fromm, type_), 5)
        
    def _messageRecieved(self, conn, message):
        sender = message.getFrom().getStripped()
        receiver = message.getTo().getStripped()
        resource = message.getFrom().getResource()
        messageid = message.getID()
        message = message.getBody()
        
        
        q.logger.log('Message is received, from:%s, to:%s, id:%s, body:%s'%(sender, receiver, messageid, message)) 
        
        messageHanlder = XMPPMessageHandler()
        messageObject = messageHanlder.deserialize(sender, receiver, resource, messageid, message)
        
        callback = self.callbacks[messageObject.type_]
        if callback:
            callback(messageObject)
        else:
            q.logger.log("Warning, no callback is registered for type:%s"%messageObject.type_)
            
            
    def disconnect(self):
        """
        Disconnects the client to xmpp server with the credentials specified

        @return:                     True in case disconnecting succeeded
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """
        if self.status == 'NOT_CONNECTED':
            q.logger.log('Client is already not connected')
            return True
        
        q.logger.log("Stopping the xmpp client to %s at server: %s"%(self.userJID, self.server), 5)
        self._client.disconnect()
        self.status = 'NOT_CONNECTED'
        return True

    def sendPresence(self, to=None, type_=None):
        ''' Send a presence
        @param to: The userJID of the client to send the presence to. None=send to all your friends
        @type to: string
        @param type: The type of the presence. Possible values: None=available, unavailable, subscribe, subscribed 
        @type type: string
        '''
        if self.status <> 'RUNNING' and self.status <> 'CONNECTED':
            q.logger.log("Client is not connected")
            return
        
        q.logger.log("Sending presence of type %s to %s"%(str(type_), str(to)), 5)
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
            q.logger.log("Client is not connected")
            return
        
        sender = xmppmessage.sender
        receiver = xmppmessage.receiver
        resource = xmppmessage.resource 
        
        if not isinstance(xmppmessage, XMPPLogMessage):
            q.logger.log("Sending message [%s] from:%s to:%s'"%(str(xmppmessage), sender, receiver),5)
        msg = xmpp.Message(to = '%s/%s'%(receiver, resource), body = str(xmppmessage), typ = 'chat')
        msg.setID(xmppmessage.messageid)            
        return self._client.send(msg)
    
    
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
    """
    Serialize and Deserialize the XMPPMessage object to/from Pylabs XMPP message format
    """    
    
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
        
        return xmppmessage.format()
        
    def deserialize(self, sender, receiver, resource, messageid, message):
        """
        Deserializes a PyLabs XMPP command message to a XMPPMessage object
        
        @param message:              String containing command in PyLabs XMPP message format
        @type message:               string
        
        @return:                     XMPPMessage object
        @rtype:                      XMPPMessage
        """
        message = message or '' # to avoid None message sent while is typing event
        message = message.strip()
        try:            
            if message.startswith(BEGIN_RESULT): # we must check on result before checking on command prefix
                index = message.find('\n')            
                tasknumber, returncode = message[len(BEGIN_RESULT):index].split()
                returnvalue = message[index+1:-len(END_RESULT)]
                return XMPPResultMessage(sender, receiver, resource, messageid, tasknumber, returncode, returnvalue)
            elif message.startswith(BEGIN_COMMAND):# !<command> [subcommand]\n[params]*\n!
                index = message.find('\n')                     
                commandLine = message[len(BEGIN_COMMAND):index].split()
                command = commandLine.pop(0)
                subcommand = commandLine[0] if commandLine else ''            
                args, options= self._getArgumentsAndOptions(message[index+1:])
                return XMPPCommandMessage(sender, receiver, resource, messageid, command, subcommand, {'params':args, 'options':options})
            elif message.startswith(BEGIN_LOG): # @<tasknr>|<logentry>            
                index = message.find('|')
                tasknumber = message[1:index]
                logentry = message[index+1:]
                return XMPPLogMessage(sender, receiver, resource, messageid, tasknumber, logentry)
            elif message.startswith(BEGIN_TASKNR):# <ID>Tasknumber          
                tasknumber = message[len(BEGIN_TASKNR):]
                return XMPPTaskNumberMessage(sender, receiver, resource, messageid, tasknumber)
            else:
                return XMPPMessage(sender, receiver, resource, messageid, message)
        except Exception:
            return XMPPMessage(sender, receiver, resource, messageid, message)
        
    
    def _getArgumentsAndOptions(self, commandInput): 
        """
        Parse the Arguments and options out of the commandInputs
                
        """
        args = commandInput.split("$")
        argsResult = list()
        options = list()
        def mod(arg):
            arg = arg[:-1]
            if arg[:1] == '-':
                options.append(arg.strip())                
            else:
                argsResult.append(arg.strip())                
        
        filter(mod, args)
        return argsResult, options
    
class XMPPMessage(object):
    """
    Class representing a generic PyLabs XMPP message
    """
    type_ = TYPE_UNKNOWN
    def __init__(self, sender, receiver, resource, messageid, message):
        self.sender = sender
        self.receiver = receiver
        self.resource = resource
        self.messageid = messageid
        self.message = message
        
    def format(self):
        return self.message
    
    def __str__(self):
        return self.format()

class XMPPCommandMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP command message
    """
    type_ = TYPE_COMMAND    
    def __init__(self, sender, receiver, resource, messageid, command, subcommand='', params=None):
        self.sender = sender
        self.receiver = receiver
        self.resource = resource
        self.messageid = messageid
        self.command = command
        self.subcommand = subcommand
        self.params = params
    
    def format(self):            
        params = self.params['params'] + self.params['options'] if self.params else list()
        return '%(begin)s%(command)s %(subcommand)s\n%(params)s\n%(end)s'%{'begin':BEGIN_COMMAND, 'end':END_COMMAND, 'command':self.command, 'subcommand':self.subcommand, 'params':'\n$'.join(params)}
    
    def __str__(self):
        return self.format()       
                


class XMPPResultMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP result message
    """
    type_ = TYPE_RESULT
    def __init__(self, sender, receiver, resource, messageid, tasknumber, returncode, returnvalue):
        
        self.sender = sender
        self.receiver = receiver
        self.resource = resource
        self.messageid = messageid
        self.tasknumber = tasknumber
        self.returncode = returncode
        self.returnvalue = returnvalue
        
    def format(self):
        return '%(begin)s%(tasknumber)s %(returncode)s\n%(returnvalue)s\n%(end)s'%{'begin':BEGIN_RESULT, 'end':END_RESULT, 'tasknumber':self.tasknumber, 'returncode':self.returncode, 'returnvalue':self.returnvalue}    
    
    def __str__(self):
        return self.format() 


class XMPPLogMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP log message
    """
    type_ = TYPE_LOG
    def __init__(self, sender, receiver, resource, messageid, tasknumber, logentry):
        self.sender = sender
        self.receiver = receiver
        self.resource = resource
        self.messageid = messageid
        self.tasknumber = tasknumber
        self.logentry = logentry
        
    def format(self):
        return '@%s|%s'%(self.tasknumber, self.logentry)
    
    def __str__(self):
        return self.format()


class XMPPErrorMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP error message
    """
    type_ = TYPE_ERROR
    def __init__(self, sender, receiver, resource, messageid, tasknumber, returncode, returnvalue):
        pass

class XMPPTaskNumberMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP error message
    """
    type_ = TYPE_TASKNUMBER
    def __init__(self, sender, receiver, resource, messageid, tasknumber):
        self.sender = sender
        self.receiver = receiver
        self.resource = resource
        self.messageid = messageid
        self.tasknumber = tasknumber
    
    def format(self):
        return '%(begin)s%(tasknumber)s'%{'begin':BEGIN_TASKNR, 'tasknumber':self.tasknumber}
    
    def __str__(self):
        return self.format()
    