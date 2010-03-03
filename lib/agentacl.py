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

'''
PyLabs agent authentication / authorization module
'''

from pymonkey.inifile import IniFile
from pymonkey import q

import re
import os


class AgentACL(object):
    '''
    classdocs
    '''
    
    def __init__(self, agentname, domain, aclConfig = None):
        '''
        Constructor
        
        @param agentname: name of xmpp account
        @type agentname: string
        
        @param domain: domain of the account on the ejabber server
        @type doamin: string 
        
        @param aclConfig: list fo acl configuration for the account
        @type aclConfig: list of dict 
        
        '''
        
        """
        * Reads ACLs for the account specified from agent config file
        * Fills dict where key is agentfilter (if multiple, create multiple items in dict) and value is a dict of allow actions
        E.g.
        
        {
            "*@noc.sso.daas.com": {'system/remote/portforward': True, 'qpackages/update': False},
            "agentcontroller@domain.com": {'system/*': True, 'qpackages/*': True, 'agent/*': True}
        }
        
        
        * Remarks:
        ** Key can exist in multiple ACLs!
        ** ACLs may be contradictory. && in other words
        """
        self.aclRules = dict()
        if not aclConfig:
            aclConfig = list()
        self.aclConfig = aclConfig
        self.agentname = agentname
        self.domain = domain
        self._processAclConfig()
    
    
    def isAuthenticated(self, agent):
        """
        Checks if the remote agent is authenticated by the current agent
        
        @param agent:                JID of remote agent 
        @type agent:                 string

        @return:                     True is case agent is authenticated, False if not
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

        return not self._resolveAuthenticatedAgent(agent) == None

    def isAuthorized(self, agent, path):
        """
        Checks if the remote agent is authorized the execute the tasklet for the path specified 
        
        @param agent:                JID of remote agent 
        @type agent:                 string

        @param path:                 Path on file system where matched tasklet is located 
        @type path:                  string

        @return:                     True is case agent is authenticated, False if not
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

        result = self._resolveAuthenticatedAgent(agent)
        if not result:
            return False 
        
        """
        ** If agent found
        *** Search for exact path
        **** If not found, see if wild-card path is found
        ***** E.g. ACL may not contain path system/qshellcmd but might contain system/*
        """
        path = self._getRelativePath(path)
        if path in result:
            return result[path]
        itemsWithWildCards = filter(lambda x: x[0].find('*') != 0, result.items())
        result = False
        for key, value in itemsWithWildCards:
            pattern = re.compile('%s$'%key.replace('*', '.*'))
            match = pattern.match(path)
            if match:
                result =  value
                break
        return result
                
    
    def _getRelativePath(self, path):
        """
        Retrieves the relative path of the tasklet path
        """
        commandsPath = q.system.fs.joinPaths(q.dirs.appDir, 'agent', 'cmds')
        relativePath = path.split(commandsPath)[-1]
        dotIndex = relativePath.rfind('.')
        return relativePath[len(os.sep) if relativePath.startswith(os.sep) else 0: relativePath.rindex('.') if dotIndex != -1  else len(relativePath)]
        
        
    
    def _resolveAuthenticatedAgent(self, agent):
        """
        * Search in ACL dict if agent with full name is authenticated
        ** If not, see if agent meets wild-card authentication
        *** E.g. ACL may not contains agentfilters for agent robot001@noc.sso.daas.com but might contain entry for *@noc.sso.daas.com
        
        * Return item found or None in case no match was found 
        """
        item = None
        if agent in self.aclRules:
            return self.aclRules[agent]
        
        itemsWithWildCards = filter(lambda x : x[0].find('*') != -1, self.aclRules.items())
        for key, value in itemsWithWildCards:
            pattern = re.compile('%s$'%key.replace('*', '.*'))
            match = pattern.match(agent)
            if match:
                item = value
                break
        return item
            
        
    
    def _processAclConfig(self):
        """
        Process acl configuration list for an account, retrieves all the acls for this account and fills the aclRuls dict with the result
        """
        
        for aclInfo in self.aclConfig:
            jids = aclInfo['agentfilters'].split(',')
            aclInfo.pop('agentfilters')
            for jid in jids:
                jid = jid.strip()
                if jid:
                    self._updateRules(jid, aclInfo)
        
                    
    def _updateRules(self, jid, aclInfo):
        """
        Update the acls rules of a filter entry with the new acl info, if the filter already exists it will update the current 
        acl entry by && the existing acls for this filter, and adding new key and values for the filter if not exist
        
        @param jid: the filter jid
        @param aclInfo: the acl info as dict
        """
        if not jid in self.aclRules.keys():
            self.aclRules[jid] = dict()
            
        for key, value in aclInfo.items():
            if key in self.aclRules[jid]:
                #if the rule already exist take the most pessimistic one, in other words &&
                self.aclRules[jid][key] = self.aclRules[jid][key] and bool(int(value))
            else:
                self.aclRules[jid][key] = bool(int(value)) 
        
        
    
        
        