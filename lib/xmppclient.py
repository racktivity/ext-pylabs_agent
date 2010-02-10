'''
PyLabs XMPP client module
'''

class XMPPClient(object):
    '''
    classdocs
    '''
    def __init__(self, jid, password, resource=None):
        '''
        Constructor
        @param jid:                  XMPP JID
        @type jid:                   string

        @param password:             Password
        @type password:              string

        @param resource:             Resource name
        @type resource:              string
        '''
        pass
     
    def connect(self, server=None):
        """
        Connects the client to xmpp server with the credentials specified

        @param server:               If specified, connect to a specific server hosting the domain 
        @type server:                string

        @return:                     True in case of successful connection
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

    def disconnect(self):
        """
        Disconnects the client to xmpp server with the credentials specified

        @return:                     True in case disconnecting succeeded
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

    def sendMessage(self, xmppmessage):
        """
        @param xmppmessage           XMPP message
        @type xmppmessage            XMPPMessage

        @return:                     Unique identifier for this message
        @rtype:                      string

        @raise e:                    In case an error occurred, exception is raised
        """        
        pass
    
    def setCommandReceivedCallback(self, commandHandler):
        """
        @param logHandler:           Callable which is called whenever a command message is received.
        @type logHandler:            callable
        @note:                       Interface for the callable must be (XMPPCommandMessage)
        """

    def setLogReceivedCallback(self, logHandler):
        """
        @param logHandler:           Callable which is called whenever a log message is received.
        @type logHandler:            callable
        @note:                       Interface for the callable must be (XMPPLogMessage)
        """

    def setErrorReceivedCallback(self, errorHandler):
        """
        @param errorHandler:         Callable which is called whenever a error message is received.
        @type errorHandler:          callable
        @note:                       Interface for the callable must be (XMPPErrorMessage)
        
        """

    def setResultReceivedCallback(self, resultHandler):
        """
        @param resultHandler:        Callable which is called whenever a result message is received.
        @type resultHandler:         callable
        @note:                       Interface for the callable must be (XMPPResultMessage)
        """

    def setMessageReceivedCallback(self, messageHandler):
        """
        @param messageHandler:       Callable which is called whenever a message is received.
        @type messageHandler:        callable
        @note:                       Interface for the callable must be (XMPPMessage)
        """

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
        
    def deserialize(self, message):
        """
        Deserializes a PyLabs XMPP command message to a XMPPMessage object
        
        @param message:              String containing command in PyLabs XMPP message format
        @type message:               string
        
        @return:                     XMPPMessage object
        @rtype:                      XMPPMessage
        """
    
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
    def __init__(self, sender, receiver, messageid, command, params=[]):
        pass

class XMPPResultMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP result message
    """
    def __init__(self, sender, receiver, messageid, tasknumber, returncode, returnvalue):
        pass

class XMPPLogMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP log message
    """
    def __init__(self, sender, receiver, messageid, tasknumber, logentry):
        pass

class XMPPErrorMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP error message
    """
    def __init__(self, sender, receiver, messageid, tasknumber, returncode, returnvalue):
        pass

class XMPPTaskNumberMessage(XMPPMessage):
    """
    Class representing a PyLabs XMPP error message
    """
    def __init__(self, sender, receiver, messageid, tasknumber):
        pass

    