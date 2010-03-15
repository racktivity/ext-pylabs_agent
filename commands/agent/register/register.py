__author__ = 'incubaid'
__tags__ = 'agent', 'register'
__priority__= 1

import random

AGENT_CONTROLLER_JID = 'agentcontroller'
BEGIN_RESULT = '!!!'
END_RESULT = '!!!'

def _parseResult(result, timeout):
    """
    parses the result message and extract the returncode and returnvalue of the message 
    """
    beginIndex = result.find(BEGIN_RESULT)
    if  beginIndex == -1:
        raise RuntimeError("Failed to get response from %s in %d seconds"%(AGENT_CONTROLLER_JID, timeout))
    result = result[beginIndex:]
    index = result.find('\n')            
    _, returncode = result[len(BEGIN_RESULT):index].split()
    returnvalue = result[index+1:-len(END_RESULT)]
    return int(returncode), returnvalue
    
    
def _generateUniqueAccountName(config):
    """
    Generate account name and make sure that the new accountname is unique within this agent
    """
    number = random.randint(0, 1000)
    accountName = 'account_account%d'%number
    while accountName in config:
        number = random.randint(0, 1000)
        accountName = 'account_account%d'%number
    return accountName
    

def main(q, i, params, tags):
    q.logger.log("agent register params:%s tags:%s"%(params,tags), 5)
    args = params['params']
    timeout = 10 #maybe we should task this from the params
    if not len(args) in (2, 4):
        raise RuntimeError('Invalid number of arguements, the command needs either 2 or 4 arguments')
    if len(args) == 4:
        xmppserver, domain, agentname, password = args
        anonymousPassword = 'test'
        xmppConnection = q.clients.xmpp.getConnection(None, anonymousPassword, xmppserver, domain)
        result = xmppConnection.sendCommand('%s@%s'%(AGENT_CONTROLLER_JID, domain), category = 'domaincontroller', method = 'register', params = [agentname, password, domain], timeout = timeout)
        returncode, returnvalue = _parseResult(result, timeout)
        if returncode:
            raise RuntimeError("Failed to register user %s with server %s. Reason %s"%('%s@%s'%(agentname, domain), xmppserver, returnvalue))
        
        agentConfig = q.config.getConfig('agent') if 'agent' in q.config.list() else None
        if not agentConfig:
            
            raise RuntimeError('Cannot find agent config file')
        accountName = _generateUniqueAccountName(agentConfig)
        newConfigEntry = {'agentname': agentname, 'domain': domain, 'server': xmppserver, 'password': password, 'enabled': 1}
        agentInifile = q.config.getInifile('agent')
        agentInifile.addSection(accountName)
        for key, value in newConfigEntry.items():
            agentInifile.setParam(accountName, key, value)
        params['returncode'] = 0
        params['returnvalue'] = 'Successfully registered new account with jid %s on server %s'%('%s@%s'%(agentname, domain), xmppserver)
    q.logger.log("Restarting the agent daemon..", 5)
    q.kernel.agent.stop()
    q.kernel.agent.start()

def match(q, i, params, tags):
    return True
