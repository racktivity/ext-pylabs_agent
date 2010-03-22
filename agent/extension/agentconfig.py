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

import pymonkey
from pymonkey.config import *
from pymonkey import q

class AgentAccountsConfigItem(ConfigManagementItem):
    """
    Configuration of the agent.
    """

    CONFIGTYPE = "agent_accounts"
    DESCRIPTION = "agent account section"

    def ask(self):
        self.dialogAskString('agentname', 'agent name', 'test')
        self.dialogAskPassword('password', 'agent password', 'test')
        self.dialogAskString('domain', 'agent domain', 'dmachine.sso.daas.com')
        self.dialogAskString('server', 'ejabberd server', 'dmachine.sso.daas.com')
        self.dialogAskString('agentcontrollername', 'agent controller name', 'agentcontroller')
        self.dialogAskYesNo('anonymous', 'Register this account on server?', False)
        self.dialogAskYesNo('enabled', 'Is the agent account enabled', True)
        
AgentAccountsConfig = ItemGroupClass(AgentAccountsConfigItem)

class AgentAclsConfigItem(ConfigManagementItem):
    """
    Configuration of the agent.
    """

    CONFIGTYPE = "agent_acls"
    DESCRIPTION = "agent acl section"

    def ask(self):
        self.dialogAskString('account_name', 'enter account section name for the new acl')
        self.dialogAskString('agentfilters', 'enter filter for the allowed agent(s)', '*@dmachine.sso.daas.com')
        commandGroups = map(lambda x:  "%s/*"%q.system.fs.getBaseName(x), q.system.fs.listDirsInDir(q.system.fs.joinPaths(q.dirs.appDir, 'agent', 'cmds')))
        for commandGroup in commandGroups:
            self.dialogAskYesNo(commandGroup, 'enable command group:%s ?'%commandGroup[:-2], True)
            
    def save(self):        
        file = q.config.getInifile(self.configtype)
        if not file.checkSection(self.itemname):
            file.addSection(self.itemname)
        for k, v in self.params.iteritems():
            file.setParam(self.itemname, k, v)
        file.write() 
        
AgentAclsConfig = ItemGroupClass(AgentAclsConfigItem)                