import os, xmlrpclib
import base64

class AgentLogTarget(object):
    def __init__(self, serverIp='127.0.0.1', serverPort='8888', serverPath = '/', maxVerbosityLevel=1):
        self.serverIp = serverIp
        self.serverPort = serverPort
        self.serverPath = serverPath
        self.maxVerbosityLevel = maxVerbosityLevel
        self.connection = xmlrpclib.ServerProxy('http://%s:%s%s/'%(self.serverIp, self.serverPort, self.serverPath))
        self.pid = os.getpid()

    def __str__(self):
        return "AgentControllerLogTarget logging to %s:%s"%(self.serverIp, self.serverPort)

    def ___repr__(self):
        return str(self)

    def log(self, message):
        msg = base64.encodestring(record.msg)
        self.connection.agent_service.log(self.pid, record.verbosityLevel, msg)
