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


class AgentACL(object):
    '''
    classdocs
    '''
    
    def __init__(self, agentname, domain):
        '''
        Constructor
        
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
        self._parseConfigFile(agentname, domain)
    
    
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
        """
        ** If agent found
        *** Search for exact path
        **** If not found, see if wild-card path is found
        ***** E.g. ACL may not contain path system/qshellcmd but might contain system/*
        """
        if result:
            item = result.get(path, None)
            if item == None:
                itemsWithWildCards = filter(lambda x: x[0].find('*') != 0, result.items())
                for key, _ in itemsWithWildCards:
                    pattern = re.compile('%s$'%key.replace('*', '.*'))
                    match = pattern.match(path)
                    if match:
                        return True
            else:
                return item
        return False
                    
        
    
    def _resolveAuthenticatedAgent(self, agent):
        """
        * Search in ACL dict if agent with full name is authenticated
        ** If not, see if agent meets wild-card authentication
        *** E.g. ACL may not contains agentfilters for agent robot001@noc.sso.daas.com but might contain entry for *@noc.sso.daas.com
        
        * Return item found or None in case no match was found 
        """
        
        item = self.aclRules.get(agent, None)
        if not item:
            itemsWithWildCards = filter(lambda x : x[0].find('*') != -1, self.aclRules.items())
            for key, value in itemsWithWildCards:
                pattern = re.compile('%s$'%key.replace('*', '.*'))
                match = pattern.match(agent)
                if match:
                    item = value
                    break
        return item
            
        
    def _parseConfigFile(self, agentname, domain):
        """
        Parses the agent config file and constructs a dictionary of dictionaries
        
        @param agentname: name of the agent
        @param domain: agent domain
        """
        if not 'agent' in q.config.list():
            raise RuntimeError('Agent config file does not exit')
        agentConfig = q.config.getConfig('agent')
        for section in filter(lambda item: item != 'main', agentConfig.keys()):
            sectionInfo = agentConfig.get(section)
            if sectionInfo.get('agentname', False) == agentname and sectionInfo.get('domain', False) == domain:
                self._processSection(agentConfig, section)
            
    
    def _processSection(self, agentConfig, section):
        """
        Process an account section, retrieves all the acls for this account and fills the aclRuls dict with the result
        
        @param agentConfig: the agent config as dictionary
        @param section: section to process
        """
        accountAcls = filter(lambda x : x.startswith('%s_'%section), agentConfig.keys()) # '%s_'%section to prevent the account itself from appearing in the list
        for accountAcl in accountAcls:
            aclInfo = agentConfig.get(accountAcl)
            filters = aclInfo['agentfilters'].split(',')
            for filterEntry in filters:
                filterEntry = filterEntry.strip() # takes care of the leading, trailing whitespace in the comma sperated list of filters
                if filterEntry:
                    self._updateRules(filterEntry, aclInfo)
                    
                    
    def _updateRules(self, filterEntry, aclInfo):
        """
        Update the acls rules of a filter entry with the new acl info, if the filter already exists it will update the current 
        acl entry by && the existing acls for this filter, and adding new key and values for the filter if not exist
        
        @param filterEntry: the filter entry
        @param aclInfo: the acl info as dict
        """
        filterValue = aclInfo.pop('agentfilters')
        if not filterEntry in self.aclRules.keys():
            self.aclRules[filterEntry] = dict()
            
        for key, value in aclInfo.items():
            if key in self.aclRules[filterEntry].keys():
                #if the rule already exist take the most pessimistic one, in other words &&
                self.aclRules[filterEntry][key] = self.aclRules[filterEntry][key] and bool(int(value))
            else:
                self.aclRules[filterEntry][key] = bool(int(value)) 
        aclInfo['agentfilters'] = filterValue
        
        