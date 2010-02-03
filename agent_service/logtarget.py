import os, xmlrpclib
import base64
from pymonkey import q
from pymonkey.logging.LogObject import LogObject

class AgentLogTarget(object):
    def __init__(self, serverIp='127.0.0.1', serverPort='8888', serverPath = '/', maxVerbosityLevel=8):
        self.serverIp = serverIp
        self.serverPort = serverPort
        self.serverPath = serverPath
        self.maxVerbosityLevel = maxVerbosityLevel
        self.connection = xmlrpclib.ServerProxy('http://%s:%s%s/'%(self.serverIp, self.serverPort, self.serverPath))
        self.pid = os.getpid()
        self.enabled = True

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        True

    def __str__(self):
        return "AgentControllerLogTarget logging to %s:%s"%(self.serverIp, self.serverPort)

    def ___repr__(self):
        return str(self)
    
    def log(self, message):
        #logmsg = q.logger.getLogObject(message)
        logmsg = LogObject(message)
        msg = base64.encodestring(logmsg.message)
        
        self.connection.agent_service.log(self.pid, logmsg.level, msg)
        return True

class XMPPLogTarget(object):
    def __init__(self, agent,  maxVerbosityLevel=5):
        self._agent = agent 
        self.enabled = True
        self.maxVerbosityLevel = maxVerbosityLevel

    def checkTarget(self):
        """
        check status of target, if ok return True
        for std out always True
        """
        True

    def __str__(self):
        return 'XMPPLogTarget'

    def ___repr__(self):
        return str(self)

    def log(self, message):
        #logmsg = q.logger.getLogObject(message)
        logmsg = LogObject(message)        
        tags = q.base.tags.getObject(logmsg.tags)
        if tags.tagExists('tasknr'):
            tasknr = tags.tagGet('tasknr')        
            self._agent.log(tasknr=tasknr, message=logmsg.message)
        
        return True

        