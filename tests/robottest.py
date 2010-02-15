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

parentFolder = q.system.fs.getDirName(__file__)[:-1]
sys.path.append(q.system.fs.joinPaths(parentFolder[:parentFolder.rindex(os.sep)], 'lib'))

from robot import Robot


testTaskletContent = \
"""
__tags__ = 'test'
__priority__ = 1


def match(q, i, params, tags):
    q.logger.log("Test Tasklet, match,  params:%s tags:%s"%(params,tags))
    return True

def main(q, i, params, tags):
    q.logger.log("Test Tasklet  main, params:%s tags:%s"%(params,tags))
    
    timeslice = float(params.get('timeslice', 0.1))
    
    import time
    try:
        while True: 
            time.sleep(timeslice)
            q.logger.log('Sleeping for some good %s seconds'%timeslice, 5)
    finally:
    
        params['currentTime'] = time.ctime()
        params['result'] = 'Killed'
"""

class RobotTest(unittest.TestCase):
    
    
    def setUp(self):
        self.testTaskletDirCreated = False
        self.robot = Robot()
        self.testTaskletDir = q.system.fs.joinPaths(q.dirs.appDir, 'agent', 'cmds', 'agent')
        self.testTaskletPath = q.system.fs.joinPaths(self.testTaskletDir, 'test.py')
        if not q.system.fs.exists(self.testTaskletDir):
            q.system.fs.createDir(self.testTaskletDir)
            self.testTaskletDirCreated = True
        elif q.system.fs.exists(self.testTaskletPath):
            q.system.fs.moveFile(self.testTaskletPath, '%s.bak'%self.testTaskletPath)
        q.system.fs.writeFile(self.testTaskletPath, testTaskletContent)
    
    
    def tearDown(self):
        if q.system.fs.exists('%s.bak'%self.testTaskletPath):
            q.system.fs.moveFile('%s.bak'%self.testTaskletPath, self.testTaskletPath)
        self.testTaskletPath = None
        if self.testTaskletDirCreated:
            q.system.fs.removeDir(self.testTaskletDir)
        self.testTaskletDirCreated = False
        self.testTaskletDir = None
        del self.robot
        
    
    def testFindCommands(self):
        tags = ('test', )
        self.assertNotEqual(self.robot.findCommands(tags = tags, params = dict()), list(), 'expected list of at least one item, found empty list')
        tags = ('test1', )
        self.assertEqual(self.robot.findCommands(tags = tags, params = dict()), list(), 'expected an empty list, found list with items')
        
    def testExecute(self):
        tags = ('test', )
        params = dict()
        tasknr = self.robot.execute(tags = tags, params = params)
        self.assertNotEqual(tasknr, -1, 'expected a positive task number, got -1 instead')
        self.robot.killTask(tasknr)
        tags =  ('test1', )
        tasknr = self.robot.execute(tags = tags, params = params)
        self.assertEqual(tasknr , -1, 'expected -1, but found task with nubmer %s'%tasknr)
    
    
    def testKillTask(self):
        tags = ('test', )
        params = dict()
        tasknr = self.robot.execute(tags = tags, params = params)
        self.assertTrue(self.robot.killTask(tasknr), 'Kill task %s should be successful'%tasknr)
        self.assertEqual(params.get('result', False), 'Killed', 'the result key in the params should be killed, but params is %s'%params)
        tasknr = -1
        self.failUnlessRaises(ValueError, self.robot.killTask, tasknr)
        
    
    def runTest(self):
        self.testFindCommands()
        self.testExecute()
        self.testKillTask()
        
