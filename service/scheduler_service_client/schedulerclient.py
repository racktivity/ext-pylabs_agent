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

pylabs scheduler service client
'''

import xmlrpclib
from pymonkey import q


class SchedulerClient(object):
    def __init__(self):
        self._ip = q.config.getConfig('scheduler')['main']['xmlrpc_ip']
        portAsString = q.config.getConfig('scheduler')['main']['xmlrpc_port']
        self._port = int(portAsString) if portAsString else 0
        self._proxy = xmlrpclib.ServerProxy('http://%(ip)s:%(port)s/'%{'ip':self._ip, 'port':self._port}, allow_none=True)
    
    
    def start(self, groupname = None):
        """
        Starts a scheduler
        
        @param groupname:            Optional parameter specifying the scheduler group to start. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/ 
        @type groupname:             string

        @return:                     True if no error occurred
        @rtype:                      bool

        @raise e:                    In case an error occurred, exception is raised
        """
        return self._proxy.scheduler.start(groupname)
        
        
    def stop(self, groupname = None):
        """
        Stops an running scheduler
        
        @param groupname:            Optional parameter specifying the scheduler group to stop. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/ 
        @type groupname:             string

        @return:                     True if no errors occurred
        @rtype:                      bool

        @raise e:                    In case an error occurred, exception is raised
        """
        
        return self._proxy.scheduler.stop(groupname)
    
    
    def getStatus(self, groupname = None):
        """
        Gets the status of the scheduler
        
        @param groupname:            Optional parameter specifying the scheduler group to stop. Is name of folder on local filesystem underneath [qbase]/apps/scheduler/ 
        @type groupname:             string

        @return:                     Returns a dictionary of groupname: q.enumerators.AppStatusType
        @rtype:                      dictionary

        @raise e:                    In case an error occurred, exception is raised
        """
        
        result = self._proxy.scheduler.getStatus(groupname)
        try:
            for key, value in result.copy().iteritems():
                result[key] = q.enumerators.AppStatusType.getByName(value)
        except Exception, ex:
            q.logger.log(str(ex), 5)
        return result
    
    def getUpTime(self):
        """
        Gets the uptime of the scheduler
        
        @return:                     Time delta specifying the uptime for the scheduler
        @rtype:                      datetime.timedelta

        @raise e:                    In case an error occurred, exception is raised
        """
        return self._proxy.scheduler.getUpTime()
    
    
    def getParams(self, groupname):
        """
        Gets the parameters of the scheduler specified
        
        @param groupname:            Scheduler group for which the parameters are returned 
        @type groupname:             string

        @return:                     Dictionary of parameters
        @rtype:                      dictionary

        @raise e:                    In case an error occurred, exception is raised
        """
        
        return self._proxy.scheduler.getParams(groupname)