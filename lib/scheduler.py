# -*- coding: utf-8 -*-
'''
INCUBAID BSD version 2.0 
Copyright � 2010 Incubaid BVBA

All rights reserved. 
 
Redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following 
conditions are met: 
 
* Redistributions of source code must retain the above copyright 
notice, this list of conditions and the following disclaimer. 

* Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in    the documentation and/or other materials provided with the   distribution. 

* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
 
THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 


PyLabs agent scheduler module
'''
from killablethread import KillableThread
from pymonkey import q, i
from pymonkey.inifile import IniFile
import itertools
import time
import yaml

class Scheduler(object):
    '''
    PyLabs agent scheduler class
    '''
    def __init__(self):
        '''
        Constructor
        '''
        
        """
        Go over all folders underneath [qbase]/apps/scheduler/
        For every folder create a SchedulerGroup(folder)
        
        """
        self.runningGroups = list()
        self._startTime = time.time()
        self._schedulerPath = q.system.fs.joinPaths(q.dirs.appDir, 'scheduler')
        self.groups = dict()
        q.system.fswalker.walk(self._schedulerPath, callback=self._createGroup, arg = self.groups, includeFolders=True, recursive=False)
        
    
    
    def _createGroup(self, arg, path):
        """
        Creates a Scheduler group for the a path
        
        @param arg: argument passed throught the wallk method
        @param path: path to create scheduler 
        """
        q.logger.log('Creating Scheduler group for path %s'%path, 5)
        groupName = q.system.fs.getBaseName(path)
        arg[groupName] = SchedulerGroup(groupName, 1) #interval = 1 for testing and sould be removed
        
    
    def start(self, groupname=None):
        """
        Starts a scheduler
        
        @param groupname:            Optional parameter specifying the scheduler group to start. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/ 
        @type groupname:             string

        @return:                     Returns q.enumerators.AppStatusType
        @rtype:                      q.enumerators.AppStatusType

        @raise e:                    In case an error occurred, exception is raised
        """
        if not groupname:
            for group in self.groups:
                q.logger.log('Starting Scheduler for group %s'%group, 5)
                self.groups[group].start()
                self.runningGroups.append(group)
        elif groupname in self.groups.keys():
            q.logger.log('Starting Scheduler for group %s'%groupname, 5)
            self.groups[groupname].start()
            self.runningGroups.append(groupname)
        else:
            raise ValueError('Group %s does not exist'%groupname)
        return True
    

    def stop(self, groupname=None):
        """
        Stops an running scheduler
        
        @param groupname:            Optional parameter specifying the scheduler group to stop. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/ 
        @type groupname:             string

        @return:                     Returns q.enumerators.AppStatusType
        @rtype:                      q.enumerators.AppStatusType

        @raise e:                    In case an error occurred, exception is raised
        """
        if not groupname:
            for group in self.groups:
                q.logger.log('Stopping Scheduler for group %s'%group, 5)
                self._stopGroup(group)
                if group in self.runningGroups:
                    self.runningGroups.pop(self.runningGroups.index(group))
        elif groupname in self.groups.keys():
            q.logger.log('Stopping Scheduler for group %s'%groupname, 5)
            self._stopGroup(groupname)
            if groupname in self.runningGroups:
                self.runningGroups.pop(self.runningGroups.index(groupname))
        else:
            raise ValueError('Group %s does not exist'%groupname)
        return True
    
    
    def _stopGroup(self, groupname, timeout = 5):
        """
        Stops the thread that runs the group
        
        @param groupname: name of the group to stop
        @param timeout: the amount of time is seconds that we should wait before killing the group thread
        
        @return: True if the group stopped successfully, raise exception otherwise
        """
        if not self.getStatus(groupname).get(groupname, False) == q.enumerators.AppStatusType.RUNNING:
            q.logger.log('Scheduler for group %s is not running'%groupname, 5)
            return True
        task = self.groups[groupname]
        task.stop()
        task.join(timeout)
        if not task.stopped():
            q.logger.log('Failed to stop the group %s normally, trying to terminate the group'%groupname, 5)
            try:
                task.terminate()
            except Exception, ex:
                raise RuntimeError('Failed to terminate running group %s. Reason: %s'%(groupname, str(ex)))
        return True
        


    def getStatus(self, groupname=None):
        """
        Gets the status of the scheduler
        
        @param groupname:            Optional parameter specifying the scheduler group to stop. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/ 
        @type groupname:             string

        @return:                     Returns a dictionary of groupname: q.enumerators.AppStatusType
        @rtype:                      dictionary

        @raise e:                    In case an error occurred, exception is raised
        """
        if groupname and groupname in self.groups:
            return {groupname: q.enumerators.AppStatusType.RUNNING if groupname in self.runningGroups and self.groups[groupname].isAlive() else q.enumerators.AppStatusType.HALTED}
        return dict(zip(self.groups.keys(), map(lambda group: q.enumerators.AppStatusType.RUNNING if group in self.runningGroups and self.groups[group].isAlive() else q.enumerators.AppStatusType.HALTED, self.groups.keys())))
        
        
    def getUptime(self):
        """
        Gets the uptime of the scheduler
        
        @return:                     Time delta specifying the uptime for the scheduler
        @rtype:                      datetime.timedelta

        @raise e:                    In case an error occurred, exception is raised
        """
        return time.time() - self._startTime
    

    def getParams(self, groupname):
        """
        Gets the parameters of the scheduler specified
        
        @param groupname:            Scheduler group for which the parameters are returned 
        @type groupname:             string

        @return:                     Dictionary of parameters
        @rtype:                      dictionary

        @raise e:                    In case an error occurred, exception is raised
        """
        if not groupname in self.groups:
            raise ValueError('Group %s does not exist'%groupname)
        return self.groups[groupname].params


class SchedulerGroup(KillableThread):
    def __init__(self, groupname, interval=10):
        """
        Constructor for SchedulerGroup

        @param groupname:            Parameter specifying the scheduler group to schedule. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/
        @type groupname:             string

        @param interval:             Interval in seconds
        @type interval:              integer
        
        """
        KillableThread.__init__(self)
        
        self.groupname = groupname
        self.interval = interval
        
        
        """
        * Create tasklet engine for the group specified
        * Read parameters from $qbasedir/cfg/scheduler/$self.groupname/
        ** If params.yaml exists, deserialize + keep in memory
        ** If params.ini exists, read + keep in memory
        ** Add additional key to params dict 'STOP': self.taskletengine.STOP
        *** This will allow tasklets to stop the execution of subsequent tasklets
        """
        self.taskletengine = q.getTaskletEngine(path = q.system.fs.joinPaths(q.dirs.appDir, 'scheduler', groupname))
        self.params = self._getInitialParams(groupname)
        self.params['STOP'] = self.taskletengine.STOP
        
        
    def run(self):
        """
        import time
        while True:
            self.taskletengine.execute(self.params)
            time.sleep(self.interval)
        """
        
        while True and not self.stopped():
            self.taskletengine.execute(tags = (self.groupname, ), params = self.params)
            time.sleep(self.interval)

    
    def _getInitialParams(self, groupname):
        """
        parses the parameters file(yaml/ini) if any, and load the params in memory
        
        @param groupname: name of the group to load the params for
        """              
        params = dict()
        #if both files exist, the Yaml file supersedes the ini
        schedulerGroupPath = q.system.fs.joinPaths(q.dirs.appDir, 'schedulre', groupname)
        paramsYaml =  q.system.fs.joinPaths(schedulerGroupPath, 'params.yaml')
        paramsIni =  q.system.fs.joinPaths(schedulerGroupPath, 'params.ini')
        if q.system.fs.exists(paramsYaml):            
            file = open(paramsYaml)
            params = yaml.load(file)            
        elif q.system.fs.exists(paramsIni):
            file = IniFile(paramsIni)
            params = file.getFileAsDict()['main']
            for key, val in params.iteritems():
                # why using eval, is that only to get ride of the headache of parsing the parameters with their correct types ??
                params[key] = eval('(%s)'%val)

        return params
