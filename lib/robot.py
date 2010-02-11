'''
PyLabs robot module
'''
from threading import thread
class Robot(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        
        * Instantiates a tasklet engine for every folder underneath /apps/agent/cmds/groupname
        * Create dict for running RobotTasks
        
        '''
        pass
     
    def execute(self, tags, params=None):
        """
        Executes a tasklet in the allowed groups matching the tags and match function with the parameters specified in a separate sub-process
        
        @param tags:                 List of tags 
        @type tags:                  list

        @param params:               Dictionary of parameters 
        @type params:                dictionary

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

    def findCommands(self, tags, params=None):
        """
        Returns a list of tasklet objects which match the tags specified
        
        @param tags:                 List of tags 
        @type tags:                  list

        @param params:               Dictionary of parameters 
        @type params:                dictionary

        @return:                     List of tasklet objects
        @rtype:                      list
        
        @raise e:                    In case an error occurred, exception is raised
        """
        
        """
        Execute find method on every tasklet engine instance
        Return list of all matching tasklets
        """
    
    def killTask(self, tasknumber):
        """
        Kills the task with the number specified
        
        @param tasknumber:           Number of the task to kill
        @type tasknumber:            Integer
        
        @return:                     True in case task was killed successfully
        @rtype:                      boolean
        
        @raise e:                    In case an error occurred, exception is raised
        """
    
    def stopTask(self, tasknumber):
        """
        Stops the task with the number specified
        
        @param tasknumber:           Number of the task to stop
        @type tasknumber:            Integer
        
        @return:                     True in case task was stopped successfully
        @rtype:                      boolean
        
        @raise e:                    In case an error occurred, exception is raised
        """


class RobotTask(Thread):
    def __init__(self, taskletengine, tags, params=None):
        """
        Constructor for RobotTask

        @param taskletengine:        Tasklet engine of the corresponding tasklet to execute 
        @type taskletengine:         TaskletEngine
        
        @param tags:                 List of tags 
        @type tags:                  list

        @param params:               Dictionary of parameters 
        @type params:                dictionary

        """
        self.taskletengine = taskletengine
        self.tags = tags
        self.params = params
    def run(self):
        """
        self.taskletengine.executeFirst(self.params, self.tags)
        """
        