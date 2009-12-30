from pymonkey import q, i
from agent_service.scriptexecutor import ScriptExecutor
from pymonkey.inifile import IniFile

import time
import yaml

class Scheduler(object):
    
    def __init__(self):
        self._startTime = time.time()
        self._schedularPath =  q.system.fs.joinPaths(q.dirs.appDir, "scheduler")
        self._scriptexecutor = ScriptExecutor()
        self._tasknr = 0
        self._groupNameToTasknr = dict()        
        self._groupNameToParams = dict()
        self._ip = q.config.getConfig('applicationserver')['main']['xmlrpc_ip']
        portAsString = q.config.getConfig('applicationserver')['main']['xmlrpc_port']
        self._port = int(portAsString) if portAsString else 0
    
    def start(self, groupName=None):        
        if groupName == None: # means that we want to start all the groupNames
            q.system.fswalker.walk(self._schedularPath, callback=self._startGroup, includeFolders=True, recursive=False)
        else:
            self._startGroup(None, q.system.fs.joinPaths(self._schedularPath, groupName))
        
    def _startGroup(self, arg, groupPath):
        groupName = q.system.fs.getBaseName(groupPath)        
        if  groupName in self._groupNameToTasknr:
            q.logger.log('Process:%s is already running'%groupName)
            return
            
        script = """
import time        
import xmlrpclib
taskletEngine = q.getTaskletEngine(q.system.fs.joinPaths(r'%(schedulerPath)s', '%(groupName)s'))        
proxy = xmlrpclib.ServerProxy('http://%(ip)s:%(port)s/')        

while True:
    taskletEngine.execute(params,tags=('%(groupName)s',))
    # send updated params to our scheduler through xmlrpc
    proxy.agent_service.setParams('%(groupName)s', params)
    if 'break' in params:
        params['break'] = False 
    time.sleep(10)
"""% {'schedulerPath':self._schedularPath, 'groupName':groupName, 'ip':self._ip, 'port':self._port}         
        params = self._getInitialParams(groupName)
        params['break'] = False
        tasknr = self._generateTasknr()
        q.logger.log("DEBUG Scheduler start groupName:%s script:%s, tasknr:%s"% (groupName, script, tasknr))
        self._scriptexecutor.executeQshellCommand(groupName, tasknr, params, script, captureOutput=True, maxLogLevel=5)        
        self._groupNameToTasknr[groupName] = tasknr
        self._groupNameToParams[groupName] = params
    
    def stop(self, groupName=None):
        if groupName == None:
            groupNames = self._groupNameToTasknr.keys()
            for groupName in groupNames:
                self._stopGroup(groupName)
        else:
            self._stopGroup(groupName)    
        
    
    def _stopGroup(self, groupName):
        if groupName not in self._groupNameToTasknr:
            return
    
        tasknr = self._groupNameToTasknr[groupName]            
        self._scriptexecutor.stop(groupName, tasknr)
        del self._groupNameToTasknr[groupName]
        del self._groupNameToParams[groupName]
    
    def getStatus(self, groupName=None):        
        if groupName == None:
            status = dict()
            for groupPath in q.system.fswalker.find(self._schedularPath, recursive=False, includeFolders=True):
                groupName = q.system.fs.getBaseName(groupPath)
                status[groupName] = 'Running' if groupName in self._groupNameToParams else 'Halted'
            return status 
        else:
            return 'Running' if groupName in self._groupNameToParams else 'Halted'        
    
    def getUpTime(self):
        return time.time() - self._startTime
    
    def getParams(self, groupName):
        if groupName not in self._groupNameToParams:
            raise RuntimeError("Process:%s is not running"%groupName)
        
        return self._groupNameToParams[groupName]
    
    def setParams(self, groupName, params):
        q.logger.log('DEBUG setParam(groupName:%s, params:%s)'%(groupName, params))
        if groupName not in self._groupNameToParams:
            raise RuntimeError("Process:%s is not running"%groupName)
    
        self._groupNameToParams[groupName] = params
    
    def _generateTasknr(self):
        self._tasknr +=1 
        return str(self._tasknr)
    
    def _getInitialParams(self, groupName):
        
        def parseParam(value):            
            if not value.count(',') == 0 : # can be array
                elements = value.split(',')
                subValue = list()
                for element in elements:
                    subValue.append(parseParam(element))     
                return subValue
            else:                            
                try:
                    num = int(value)
                    return num
                except:
                    return value                
            
        params = dict()
        paramsYaml =  q.system.fs.joinPaths(q.dirs.cfgDir, 'scheduler', groupName, 'params.yaml')
        paramsIni =  q.system.fs.joinPaths(q.dirs.cfgDir, 'scheduler', groupName, 'params.ini')
        if q.system.fs.exists(paramsYaml):            
            file = open(paramsYaml)
            params = yaml.load(file)            
        elif q.system.fs.exists(paramsIni):
            file = IniFile(paramsIni)
            params = file.getFileAsDict()['main']
            for key in params:
                params[key] = parseParam(params[key])
            return params
                                
        return params