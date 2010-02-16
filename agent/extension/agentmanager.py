'''
INCUBAID BSD version 2.0 
Copyright (c) 2010 Incubaid BVBA

All rights reserved. 
 
Redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following 
conditions are met: 
 
* Redistributions of source code must retain the above copyright 
notice, this list of conditions and the following disclaimer. 

* Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in    the documentation and/or other materials provided with the   distribution. 
* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
 
THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

PyLabs agent manager module
'''

class AgentManager(object):
    '''
    Class which is used by PyLabs extension to start and stop the agent
    '''
    def __init__(self):
        '''
        Constructor
        
        '''    
    
    def start(self):
        """
        Starts the agent as a daemon.
    
        @return:                     True is case all accounts disconnected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

        """
        Implementation tip:
        -------------------
        * Use following library to run agent as daemon 
        *** -> http://pypi.python.org/pypi/python-daemon/
        """

    def stop(self):
        """
        Stops the agent daemon.
        
        @return:                     True is case all accounts disconnected successfully
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

    def getStatus(self):
        """
        Gets the status of the agent
        
        @return:                     Returns q.enumerators.AppStatusType
        @rtype:                      q.enumerators.AppStatusType

        @raise e:                    In case an error occurred, exception is raised
        """
        pass        