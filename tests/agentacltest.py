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
import sys
import os

from pymonkey import q, i

# should be able to import the module without doing the following

#parentFolder = q.system.fs.getDirName(__file__)[:-1]
#sys.path.append(q.system.fs.joinPaths(parentFolder[:parentFolder.rindex(os.sep)], 'lib'))

from agentacl import AgentACL


aclConfig = [{'agentfilters': 'ssoupdate@noc.sso.daas.com',
 'qpackages/install': '1',
 'qpackages/update': '1',
 'system/*': '1',
 'system/qshellcmd': '0',
 'system/shellcmd': '0'}, {'agentfilters': '*@noc.sso.daas.com', 'system/remote/forward': '1'}, {'agentfilters': 'ssoread@noc.sso.daas.com, ssoupdate@noc.sso.daas.com',
 'qpackages/install': '1',
 'qpackages/update': '0'}]

class AgentACLTest(unittest.TestCase):
    
    
    def setUp(self):
        self.agentname = 'domain.com'
        self.domain = 'test'
        self.agentacl = AgentACL(self.agentname, self.domain, aclConfig)
        
    
    def tearDown(self):
        del self.agentacl
        self.domain = None
        self.agentname = None
    
    def testIsAuthenticatedFullName(self):
        remoteAgentName = 'ssoread@noc.sso.daas.com'
        self.assertTrue(self.agentacl.isAuthenticated(remoteAgentName), 'Failed to authenticate full name %s'%remoteAgentName)
        remoteAgentName = 'ssoread@noc.sso.daas.com.anything'
        self.assertFalse(self.agentacl.isAuthenticated(remoteAgentName), 'Non Authenticated agent shouldnt be authenticated')
    
    def testIsAuthenticatedWithWildCard(self):
        remoteAgentName = 'ssoNotRead@noc.sso.daas.com'
        self.assertTrue(self.agentacl.isAuthenticated(remoteAgentName), 'Wild card *@sso.daas.com should match but it fails')
        remoteAgentName = 'ssoNotRead@noc.sso.daas.com.somthing'
        self.assertFalse(self.agentacl.isAuthenticated(remoteAgentName), 'wild card *@sso.daas.com shouldnt match but it does')
    
    
    def testIsAthorizedFullName(self):
        remoteAgentName = 'ssoupdate@noc.sso.daas.com'
        testpath = 'system/qshellcmd'
        self.assertFalse(self.agentacl.isAuthorized(remoteAgentName, testpath), 'remote agent %s shouldnt have authorization for path %s'%(remoteAgentName, testpath))
        testpath = 'qpackages/install'
        self.assertTrue(self.agentacl.isAuthorized(remoteAgentName, testpath), 'remote agent %s should have authorization for path %s'%(remoteAgentName, testpath))
        remoteAgentName = 'ssoupdate@noc.sso.daas.com.anything'
        self.assertFalse(self.agentacl.isAuthorized(remoteAgentName, testpath), 'remote agent %s shouldnt even be authenticated'%remoteAgentName)
        
    def testIsAuthorizedFullNameContradictionRule(self):
        remoteAgentName = 'ssoupdate@noc.sso.daas.com'
        testpath = 'qpackages/update'
        self.assertFalse(self.agentacl.isAuthorized(remoteAgentName, testpath), 'path %s has contradiction rules, it should fail in the end result'%testpath)
    
    
    def testIsAuthorizedWithWildCards(self):
        remoteAgentName = 'ssoupdate@noc.sso.daas.com'
        testpath = 'system/anything'
        self.assertTrue(self.agentacl.isAuthorized(remoteAgentName, testpath), 'path %s should match the wild card path system/* for remote agent %s'%(testpath, remoteAgentName))
        
        
    def runTest(self):
        self.testIsAuthenticatedFullName()
        self.testIsAuthenticatedWithWildCard()
        self.testIsAthorizedFullName()
        self.testIsAuthorizedFullNameContradictionRule()
        self.testIsAuthorizedWithWildCards()
