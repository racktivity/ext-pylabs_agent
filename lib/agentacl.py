'''
PyLabs agent authentication / authorization module
'''
from threading import thread
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
     
    def isAuthenticated(self, agent):
        """
        Checks if the remote agent is authenticated by the current agent
        
        @param agent:                JID of remote agent 
        @type agent:                 string

        @return:                     True is case agent is authenticated, False if not
        @rtype:                      boolean

        @raise e:                    In case an error occurred, exception is raised
        """

        #_resolveAuthenticatedAgent(agent)

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

        #_resolveAuthenticatedAgent(agent)
        """
        ** If agent found
        *** Search for exact path
        **** If not found, see if wild-card path is found
        ***** E.g. ACL may not contain path system/qshellcmd but might contain system/*
        """
    
    def _resolveAuthenticatedAgent(self, agent):
        """
        * Search in ACL dict if agent with full name is authenticated
        ** If not, see if agent meets wild-card authentication
        *** E.g. ACL may not contains agentfilters for agent robot001@noc.sso.daas.com but might contain entry for *@noc.sso.daas.com
        
        * Return item found or None in case no match was found 
        """
        
