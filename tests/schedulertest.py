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


Test for PyLabs agent scheduler module
'''

import unittest
import time

from pymonkey import i, q

#should be able to import the module without doing the following
#import sys, os
#
#parentFolder = q.system.fs.getDirName(__file__)[:-1]
#sys.path.append(q.system.fs.joinPaths(parentFolder[:parentFolder.rindex(os.sep)], 'lib'))

from scheduler import Scheduler

class SchedulerTest(unittest.TestCase):
    
    def setUp(self):
        self.schedulerPath = q.system.fs.joinPaths(q.dirs.appDir, 'scheduler')
        if q.system.fs.exists(self.schedulerPath):
            q.system.fs.moveDir(self.schedulerPath, '%s.bak'%self.schedulerPath)
        self.moduleDir = q.system.fs.getDirName(__file__)[:-1]
        q.system.fs.copyDirTree(q.system.fs.joinPaths(self.moduleDir, 'scheduler'), self.schedulerPath)
        self.scheduler = Scheduler()
    
    
    def tearDown(self):
        q.system.fs.removeDirTree(self.schedulerPath)
        self.moduleDir = None
        if q.system.fs.exists('%s.bak'%self.schedulerPath):
            q.system.fs.moveDir('%s.bak'%self.schedulerPath, self.schedulerPath)
        self.schedulerPath = None

    
    def testGetUptime(self):
        self.assertNotEqual(self.scheduler.getUptime(), 0, 'Scheduler up time should be greater than 0')
    
    def testStart(self):
        #we have two groups in the directory we copied in the test setup, the groups are (breaktest, monitoring)
        self.scheduler.stop()
        status = self.scheduler.getStatus()
        self.assertNotEqual(status.get('breaktest', False), q.enumerators.AppStatusType.RUNNING, 'status of breaktest group should not be running')
        self.assertNotEqual(status.get('monitoring', False), q.enumerators.AppStatusType.RUNNING, 'status of monitoring group should not be running')
        #starting all the groups
        self.assertTrue(self.scheduler.start(), 'Starting of all groups should return True')
        status = self.scheduler.getStatus()
        self.assertEqual(status.get('breaktest', False), q.enumerators.AppStatusType.RUNNING, 'status of breaktest group should  be running')
        self.assertEqual(status.get('monitoring', False), q.enumerators.AppStatusType.RUNNING, 'status of monitoring group should  be running')
        
        #trying to start a group by name, one that already running
        self.assertTrue(self.scheduler.start('breaktest'), 'starting already running group should not fail')
        status = self.scheduler.getStatus()
        self.assertEqual(status.get('breaktest', False), q.enumerators.AppStatusType.RUNNING, 'status of breaktest group should not running')
        
        #trying to start a non existing group
        self.failUnlessRaises(ValueError, self.scheduler.start, 'nonexistinggroup')
        
        self.scheduler.stop()
    
    def testStop(self):
        #we have two groups in the directory we copied in the test setup, the groups are (breaktest, monitoring)
        status = self.scheduler.getStatus()
        self.assertNotEqual(status.get('breaktest', False), q.enumerators.AppStatusType.RUNNING, 'status of breaktest group should not be running')
        self.assertNotEqual(status.get('monitoring', False), q.enumerators.AppStatusType.RUNNING, 'status of monitoring group should not be running')
        
        #try to stop a not running group, shouldnt be a problem
        self.assertTrue(self.scheduler.stop('monitoring'), 'stopping a not running group should not fail')
        
        #try to stop a group that does not exit
        self.failUnlessRaises(ValueError, self.scheduler.stop, 'nonexistinggroup')
        
        self.scheduler.start()
        
        status = self.scheduler.getStatus()
        self.assertEqual(status.get('breaktest', False), q.enumerators.AppStatusType.RUNNING, 'status of breaktest group should be running')
        self.assertEqual(status.get('monitoring', False), q.enumerators.AppStatusType.RUNNING, 'status of monitoring group should be running')
        
        #try to stop a group by name
        self.assertTrue(self.scheduler.stop('monitoring'), 'stopping of running group by name should not fail')
        status = self.scheduler.getStatus()
        self.assertEqual(status.get('breaktest', False), q.enumerators.AppStatusType.RUNNING, 'status of breaktest group should be running')
        self.assertNotEqual(status.get('monitoring', False), q.enumerators.AppStatusType.RUNNING, 'status of monitoring group should not be running')
        
        #try to stop without groupname
        self.assertTrue(self.scheduler.stop(), 'stopping all groups should not fail')
        status = self.scheduler.getStatus()
        self.assertNotEqual(status.get('breaktest', False), q.enumerators.AppStatusType.RUNNING, 'status of breaktest group should not be running')
        self.assertNotEqual(status.get('monitoring', False), q.enumerators.AppStatusType.RUNNING, 'status of monitoring group should not be running')
        
        
    def testGetStatus(self):
        #we have two groups in the directory we copied in the test setup, the groups are (breaktest, monitoring)
        self.scheduler.start()
        status = self.scheduler.getStatus()
        self.assertEqual(status.get('breaktest', False), q.enumerators.AppStatusType.RUNNING, 'status of breaktest group should be running')
        self.assertEqual(status.get('monitoring', False), q.enumerators.AppStatusType.RUNNING, 'status of monitoring group should be running')
        
        #try to get status of non existing group
        self.failUnlessRaises(ValueError, self.scheduler.getStatus, 'nonexisting group')
        
        self.scheduler.stop()
        status = self.scheduler.getStatus()
        self.assertNotEqual(status.get('breaktest', False), q.enumerators.AppStatusType.RUNNING, 'status of breaktest group should not be running')
        self.assertNotEqual(status.get('monitoring', False), q.enumerators.AppStatusType.RUNNING, 'status of monitoring group should not be running')
        
    
    def testGetParams(self):
        #try to get params of non existing group
        self.failUnlessRaises(ValueError, self.scheduler.getParams, 'nonexisting group')
        
        #make sure that the STOP param is always there
        self.assertNotEqual(self.scheduler.getParams('breaktest').get('STOP', None), None, 'params should always have STOP key')
    
    
    def testSTOPEffect(self):
        #the breaktest group have two tasklets, one increment a params key called counter (breaktest0)  and the other decrement the same key (breaktest1) and set param executedonce to True
        # but the breaktest1 tasklet have lower priority and returns the STOP value, so it should only be executed once
        
        #for testing the scheduler group interval is set to 1(hardcoded)/should be parameter
        
        self.scheduler.start('breaktest')
        #wait until the scheduler loops for a couple for time
        time.sleep(5)
        params = self.scheduler.getParams('breaktest')
        self.assertFalse(params.get('breaktest1executed', False), 'params key breaktest1executed should not be True')
        self.assertNotEqual(params.get('counter', False), 0, 'params key counter should be greater than 0')
        
        self.scheduler.stop('breaktest')
        
        
    def runTest(self):
        self.testGetUptime()
        self.testGetStatus()
        self.testGetParams()
        self.testStart()
        self.testStop()
        self.testSTOPEffect()
        