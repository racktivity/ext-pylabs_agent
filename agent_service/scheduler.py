from pymonkey import q, i
from agent_service.scriptexecutor import ScriptExecutor
from pymonkey.inifile import IniFile
import itertools
import time
import yaml

class Scheduler(object):
    
    def __init__(self):
        self._startTime = time.time()
        self._schedularPath =  q.system.fs.joinPaths(q.dirs.appDir, "scheduler")
        self._scriptexecutor = ScriptExecutor(checkProgress=False)
        self._tasknr = 0
        self._groupNameToTasknr = dict()        
        self._groupNameToParams = dict()
        
        try:
            self._ip = q.config.getConfig('applicationserver')['main']['xmlrpc_ip']
            self._port= int(q.config.getConfig('applicationserver')['main']['xmlrpc_port'])
        except:
            raise RuntimeError("Error while reading application server IP/Port from config")
        
    def start(self, groupName=None):        
        if not groupName: # means that we want to start all the groupNames
            q.system.fswalker.walk(self._schedularPath, callback=self._startGroup, includeFolders=True, recursive=False)
        else:
            if groupName not in self.listGroups():
                q.logger.log('ERROR: Group:%s does not exist'%groupName)
                return
            
            self._startGroup(None, q.system.fs.joinPaths(self._schedularPath, groupName))
        
    def _startGroup(self, arg, groupPath):
        groupName = q.system.fs.getBaseName(groupPath)        
        if  groupName in self._groupNameToTasknr:
            q.logger.log('Process:%s is already running'%groupName)
            return
               
        script = open(q.system.fs.joinPaths(q.dirs.appDir, 'applicationserver', 'services', 'agent_service','schedulerLoop.py')).read()                
        self._groupNameToParams[groupName] = params = self._getInitialParams(groupName)
        params.update({'scheduler_param_schedulerPath' : self._schedularPath,
        'scheduler_param_groupName' : groupName, 
        'scheduler_param_ip' : self._ip,
        'scheduler_param_port':self._port,
        'scheduler_param_useAgentLogger' : False})
        
        params['break'] = False
        tasknr = self._generateTasknr()        
        self._scriptexecutor.executeQshellCommand(groupName, tasknr, params, script, captureOutput=True, maxLogLevel=5)        
        self._groupNameToTasknr[groupName] = tasknr

    
    def stop(self, groupName=None):
        if groupName:
            self._stopGroup(groupName)
        else:
            groupNames = self._groupNameToTasknr.keys()
            for groupName in groupNames:
                self._stopGroup(groupName)
        
    
    def _stopGroup(self, groupName):
        if groupName not in self._groupNameToTasknr:
            q.logger.log("WARNING: group name %s is not started")
            return
    
        tasknr = self._groupNameToTasknr[groupName]            
        self._scriptexecutor.stop(groupName, tasknr)
        del self._groupNameToTasknr[groupName]
        del self._groupNameToParams[groupName]
    
    
    def getStatus(self, groupName=None, includeHalted=False):        
        if groupName:
            if groupName in self.listGroups():
                status= {groupName: 'Running' if groupName in self._groupNameToParams else 'Halted' }
            else:
                q.logger.log('WARNING: group name %s does not exist'%groupName)
                status = dict()
        elif includeHalted:
            groups = self.listGroups()
            status = dict(zip(groups, map(lambda group: 'Running' if group in self._groupNameToParams else 'Halted', groups)))
        else:
            running = self._groupNameToTasknr.keys()
            status = dict(zip(running, itertools.repeat('Running', len(running))))
        return status
    
    
    def listGroups(self):
        return map(q.system.fs.getBaseName, q.system.fswalker.find(self._schedularPath, recursive=False, includeFolders=True))
        
    
    def getUpTime(self):
        return time.time() - self._startTime
    
    def getParams(self, groupName):
        if groupName not in self._groupNameToParams:
            q.logger.log('ERROR: Process:%s is not running'%groupName)
            return dict()
        
        return self._groupNameToParams[groupName]
    
    def setParams(self, groupName, params):        
        if groupName not in self._groupNameToParams:
            q.logger.log('ERROR: Process:%s is not running'%groupName)
            return            
    
        self._groupNameToParams[groupName] = params
    
    def _generateTasknr(self):
        self._tasknr +=1 
        return str(self._tasknr)
    
    def _getInitialParams(self, groupName):              
        params = dict()
        #if both files exist, the Yaml file supersedes the ini
        paramsYaml =  q.system.fs.joinPaths(q.dirs.cfgDir, 'scheduler', groupName, 'params.yaml')
        paramsIni =  q.system.fs.joinPaths(q.dirs.cfgDir, 'scheduler', groupName, 'params.ini')
        if q.system.fs.exists(paramsYaml):            
            file = open(paramsYaml)
            params = yaml.load(file)            
        elif q.system.fs.exists(paramsIni):
            file = IniFile(paramsIni)
            params = file.getFileAsDict()['main']
            for key, val in params.iteritems():
                params[key] = eval('(%s)'%val)

        return params