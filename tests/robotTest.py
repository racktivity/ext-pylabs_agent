"""
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
"""

import unittest
import sys
from pymonkey import q, i
sys.path.append(q.system.fs.joinPaths(q.system.fs.getParent(q.system.fs.getcwd()), 'lib'))
from robot import Robot

class RobotTestCase(unittest.TestCase):
    def setUp(self):
        self.robot = Robot()
        
        # creating tasklet /opt/qbase3/apps/agent/cmds/test
        testPath = q.system.fs.joinPaths(q.dirs.baseDir, 'apps', 'agent', 'cmds', 'test')
        
        if not q.system.fs.exists(testPath):
            q.system.fs.createDir(testPath)
        taskletPath = q.system.fs.joinPaths('agent','test.py')
        q.system.fs.copyFile(taskletPath, testPath)
        
        
    def runTest(self):
        tasknumber = self.robot.execute(['test'])
        self.assertNotEquals(tasknumber, None, 'tasknumber could not be None')        
        result = self.robot.killTask(tasknumber)
        self.assertTrue(result, 'Task should be killed successfully')
        
        tasknumber = self.robot.execute(['test'])
        self.assertNotEquals(tasknumber, None, 'tasknumber could not be None')
        result = self.robot.stopTask(tasknumber)
        self.assertTrue(result, 'Task should be Stopped successfully')