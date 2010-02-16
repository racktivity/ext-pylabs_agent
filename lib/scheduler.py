'''
INCUBAID BSD version 2.0 
Copyright © 2010 Incubaid BVBA

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
from threading import Thread
from datetime import datetime

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
    
    def start(self, groupname=None):
        """
        Starts a scheduler
        
        @param groupname:            Optional parameter specifying the scheduler group to start. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/ 
        @type groupname:             string

        @return:                     Returns q.enumerators.AppStatusType
        @rtype:                      q.enumerators.AppStatusType

        @raise e:                    In case an error occurred, exception is raised
        """
        pass

    def stop(self, groupname=None):
        """
        Stops an running scheduler
        
        @param groupname:            Optional parameter specifying the scheduler group to stop. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/ 
        @type groupname:             string

        @return:                     Returns q.enumerators.AppStatusType
        @rtype:                      q.enumerators.AppStatusType

        @raise e:                    In case an error occurred, exception is raised
        """
        pass


    def getStatus(self, groupname=None):
        """
        Gets the status of the scheduler
        
        @param groupname:            Optional parameter specifying the scheduler group to stop. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/ 
        @type groupname:             string

        @return:                     Returns q.enumerators.AppStatusType
        @rtype:                      q.enumerators.AppStatusType

        @raise e:                    In case an error occurred, exception is raised
        """
        pass

    def getUptime(self):
        """
        Gets the uptime of the scheduler
        
        @return:                     Time delta specifying the uptime for the scheduler
        @rtype:                      datetime.timedelta

        @raise e:                    In case an error occurred, exception is raised
        """
        pass

    def getParams(self, groupname):
        """
        Gets the parameters of the scheduler specified
        
        @param groupname:            Scheduler group for which the parameters are returned 
        @type groupname:             string

        @return:                     Dictionary of parameters
        @rtype:                      dictionary

        @raise e:                    In case an error occurred, exception is raised
        """
        pass


class SchedulerGroup(Thread):
    def __init__(self, groupname, interval=10):
        """
        Constructor for RobotTask

        @param groupname:            Parameter specifying the scheduler group to schedule. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/
        @type groupname:             string

        @param interval:             Interval in seconds
        @type interval:              integer
        
        """
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
    def run(self):
        """
        import time
        while True:
            self.taskletengine.execute(self.params)
            time.sleep(self.interval)
        """

