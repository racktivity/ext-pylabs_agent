# -*- coding: utf-8 -*-
#INCUBAID BSD version 2.0 
#Copyright © 2010 Incubaid BVBA
#
#All rights reserved. 
# 
#Redistribution and use in source and binary forms, with or 
#without modification, are permitted provided that the following 
#conditions are met: 
# 
#* Redistributions of source code must retain the above copyright 
#notice, this list of conditions and the following disclaimer. 
#
#* Redistributions in binary form must reproduce the above copyright 
#notice, this list of conditions and the following disclaimer in    the documentation and/or other materials provided with the   distribution. 
#
#* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
# 
#THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 


'''
PyLabs robot module
'''
from killablethread import KillableThread

from pymonkey import q
import time
import traceback


class Robot(object):
    '''
    Main bot classs, scans a directory and create a tasklet engine for each group of commands, executes Robot tasks
    '''
    def __init__(self):
        '''
        Constructor
        
        * Instantiates a tasklet engine for every folder underneath /apps/agent/cmds/groupname
        * Create dict for running RobotTasks
        
        '''
        self.COMMANDS = dict() 
        self.runningTasks = dict()
        self._nextTaskNumber = 1
        self._taskCompletedCallback = None
        
        q.system.fswalker.walk(q.system.fs.joinPaths(q.dirs.appDir, "agent", "cmds"), callback=self._processCommandDir, arg=self.COMMANDS, includeFolders=True, recursive=False)
    
    def _processCommandDir(self, arg, path):
        if not q.system.fs.isDir(path):
            return
        taskletEngine = q.getTaskletEngine(path)
        arg[q.system.fs.getBaseName(path)] = taskletEngine
     
    def execute(self, tags, params=None, tasknumber = None):
        """
        Executes a tasklet in the allowed groups matching the tags and match function with the parameters specified in a separate sub-process
        
        @param tags:                 List of tags 
        @type tags:                  list

        @param params:               Dictionary of parameters 
        @type params:                dictionary
        
        @param tasknumber:           number of the task to be executed
        @type tasknumber:            int

        @return:                     Task number for this task
        @rtype:                      integer

        @raise e:                    In case an error occurred, exception is raised
        """

        """
        * search for taskletengine which matches for the tags specified and which is in allowedGroups
        * create new instance of RobotTask() and pass taskletengine found above + pass tags & params
        * add RobotTask() to list of running RobotTasks
        ** self.tasks[tasknumber] = task
        * start RobotTask() in separate thread
        """
        resultEngines = self._searchTaskletEngines(tags)
        key = resultEngines.keys()[0] if resultEngines else False
        #for first iteration dont do anything if there is more than one tasklet matching the tags
        if key and (len(resultEngines.keys()) > 1 or len(resultEngines[key]) > 1):
            raise RuntimeError('More than one tasklet found for tags %s'%tags)
        elif key :
            engine = self.COMMANDS[key] 
            q.logger.log('Got taskletEngine %s for group %s'%(engine, key))
            tasknumber = tasknumber or self._generateTaskNumber()
            task = RobotTask(engine, tags, tasknumber, params)
            task.setTaskCompletedCallback(self._OnTaskCompleted)
            self.runningTasks[tasknumber] = task
            task.start()
            return tasknumber
        q.logger.log('No Tasklet found for tags %s and param %s'%(tags, params))
        return -1
        
    
    
    def getNextTaskNumber(self):
        """
        Retreive the next tasknumber in the sequence of task numbers
        """
        return self._generateTaskNumber()
    
    def _generateTaskNumber(self):
        """
        Incrementally generate task number
        """
        
        tasknumber = self._nextTaskNumber
        try:
            self._nextTaskNumber += 1
        #incase the memory of the machine is not enough for the number of take, start over
        except:
            self._nextTaskNumber = 1   
        return tasknumber 
        
        

    def findCommands(self, tags):
        """
        Returns a list of tasklet objects which match the tags specified
        
        @param tags:                 List of tags 
        @type tags:                  list


        @return:                     List of tasklet objects
        @rtype:                      list
        
        @raise e:                    In case an error occurred, exception is raised
        """
        
        """
        Execute find method on every tasklet engine instance
        Return list of all matching tasklets
        """
        result = list()
        for values in self._searchTaskletEngines(tags).values():
            result.extend([value.path for value in values])
        return result
    
    def _searchTaskletEngines(self, tags):
        """
        Search all the available tasklet engines for the matching taklets
        
        @param tags:            list of tags
        @type tags:             list
        
        @return: return a dictionary of the groupname and the tasklets matches the tags under this groupname
        """
        q.logger.log('Searching avialable tasklets engines for tasklets with tags %s '%str(tags))
        if isinstance(tags, str):
            q.logger.log('tags should be a list not string, creating a list of the input string....')
            tags = tuple([tags])
        result = dict()
        for groupName, taskletEngine in self.COMMANDS.items():
            foundTasklets = taskletEngine.find(tags = tags)
            if foundTasklets:
                result[groupName] = foundTasklets
        q.logger.log('Search results are %s'%result)
        return result          
        
    
    def killTask(self, tasknumber):
        """
        Kills the task with the number specified
        
        @param tasknumber:           Number of the task to kill
        @type tasknumber:            Integer
        
        @return:                     True in case task was killed successfully
        @rtype:                      boolean
        
        @raise e:                    In case an error occurred, exception is raised
        """
        timeout = 10 #number of seconds i will wait and check whether the thread killed or not before reporting failed termination, sould be parameter ??
        killed = False
        task = self.runningTasks.get(tasknumber, False)
        if not task:
            q.logger.log('No Task found with number %s'%tasknumber)
            return True
        if not task.isAlive():
            del self.runningTasks[tasknumber]
            q.logger.log('Task %s is terminated normally'%tasknumber)
            return True
            
        try:
            task.terminate()
        except Exception, ex:
            q.logger.log('Failed to terminate running task %s. Reason: %s'%(tasknumber, str(ex)), 3)
            traceback.print_exc()
            return False
        while timeout:
            if not task.isAlive():
                killed = True
                break
            time.sleep(1)
            timeout -= 1
        if not killed:
            q.logger.log('Failed to terminate running task %s'%tasknumber)
            return False
        del self.runningTasks[tasknumber]
        return True
        
    
    def stopTask(self, tasknumber):
        """
        Stops the task with the number specified
        
        @param tasknumber:           Number of the task to stop
        @type tasknumber:            Integer
        
        @return:                     True in case task was stopped successfully
        @rtype:                      boolean
        
        @raise e:                    In case an error occurred, exception is raised
        """
        
        #currently we dont have a way to stop a thread
        return self.killTask(tasknumber)
        
#        timeout = 5
#        task = self.runningTasks.get(tasknumber, False)
#        if not task:
#            q.logger.log('No Task found with number %s'%tasknumber)
#            raise ValueError('No task running with number %s'%tasknumber)
#        if not task.isAlive():
#            self.runningTasks.pop(tasknumber)
#            q.logger.log('Task %s is terminated normally'%tasknumber)
#            return True
#        task.stop()
#        task.join(timeout)
#        if not task.stopped():
#            q.logger.log('Failed to stop the task %s normally, trying to terminate the task'%tasknumber, 5)
#            return self.killTask(tasknumber)
#        return True


    
    def setTaskCompletedCallback(self, callback):
        """
        register a callable object that will be called upon the normal finish of task
        """
        self._taskCompletedCallback = callback

    
    
    def _OnTaskCompleted(self, tasknumber, returncode, returnvalue):
        """
        Remove compoleted task from the running tasks and triggers any registered callbacks for this event
        
        @param tasknumber: number of the task that finish
        @type tasknumber: integer
        
        @param returncode: the retrun code of the task executed, 0 means success, -1 means unknown, and anything else means failure
        @type returncode: string
        
        @param returnvalue: the return value form the completed task
        @type returnvalue: string
        """
        
        del self.runningTasks[tasknumber]
        if self._taskCompletedCallback:
            self._taskCompletedCallback(tasknumber, returncode, returnvalue)
    

class RobotTask(KillableThread):
    def __init__(self, taskletengine, tags, tasknumber, params=None):
        """
        Constructor for RobotTask

        @param taskletengine:        Tasklet engine of the corresponding tasklet to execute 
        @type taskletengine:         TaskletEngine
        
        @param tags:                 List of tags 
        @type tags:                  list
        
        @param tasknumber:           number of the task that will be executed
        @type  tasknumber:           integer

        @param params:               Dictionary of parameters 
        @type params:                dictionary

        """
        KillableThread.__init__(self)
            
        if params == None: # checking on None in case someone calling with params = dict()/{}
            params = dict()
        
        self.taskletengine = taskletengine
        if isinstance(tags, str):
            q.logger.log('tags should be a list not string, creating a list of the input string....')
            tags = tuple([tags])
        self.tags = tags or list()
        self.params = params
        self._taskCompletedCallback = None
        self.tasknumber = tasknumber
        
        
    def run(self):
        """
        self.taskletengine.executeFirst(self.params, self.tags)
        """
        self.taskletengine.execute(params = self.params, tags = self.tags)
        if self._taskCompletedCallback:
            self._taskCompletedCallback(self.tasknumber, self.params.get('returncode', -1), self.params.get('returnvalue', 'No Return Value Found'))
        
    
    def getParams(self):
        """
        Retrives the params of the current task
        """
        return self.params
    
    
    def setTaskCompletedCallback(self, callback):
        """
        Sets a callback method that will be invoked when a robot task finish normally
        
        @param callback: python callable object that will be invoked
        """
        
        self._taskCompletedCallback = callback
    
