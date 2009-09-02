import os, xmlrpclib
from pymonkey.log.LogTargets import LogTarget

class AgentLogTarget(LogTarget):
    def __init__(self, serverIp='127.0.0.1', serverPort='8888', maxVerbosityLevel=5):
        LogTarget.__init__(self)
        self.serverIp = serverIp
        self.serverPort = serverPort
        self.maxVerbosityLevel = maxVerbosityLevel
        self.connection = xmlrpclib.ServerProxy('http://%s:%s'%(self.serverIp, self.serverPort))
        self.pid = os.getpid()

    def __str__(self):
        return "AgentControllerLogTarget logging to %s:%s"%(self.serverIp, self.serverPort)

    def ___repr__(self):
        return str(self)

    def log(self, record):
        self.connection.agent_service.log(self.pid, record.verbosityLevel, record.msg)
