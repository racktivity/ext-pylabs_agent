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


import unittest

from pymonkey import q, i

# should be able to import the module without doing the following
import sys, os
#
parentFolder = q.system.fs.getDirName(__file__)[:-1]
sys.path.append(q.system.fs.joinPaths(parentFolder[:parentFolder.rindex(os.sep)], 'extension'))

from agentmanager import AgentManager

class AgentManagerTest(unittest.TestCase):
    
    def setUp(self):
        self.agentmanager = AgentManager()
    
    def testStart(self):
        #make sure that the agent is not running
        self.agentmanager.stop()
        self.assertTrue(self.agentmanager.start(), 'Agent start should return True')
        self.assertEqual(self.agentmanager.getStatus(), q.enumerators.AppStatusType.RUNNING, 'Agent status should be running')
        
        #starting an already running agent
        self.assertTrue(self.agentmanager.start(), 'Starting already running agent should return True')
        
        self.agentmanager.stop()
        
    
    def testStop(self):
        #make sure that the agent is not stopped
        self.agentmanager.start()
        self.assertTrue(self.agentmanager.stop(), 'Agent stop should return True')
        self.assertNotEqual(self.agentmanager.getStatus(), q.enumerators.AppStatusType.RUNNING, 'Agent status should not be running')
        
        #starting an already stopped agent
        self.assertTrue(self.agentmanager.stop(), 'Stopping already stopped agent should return True')
        
    def runTest(self):
        self.testStart()
        self.testStop()