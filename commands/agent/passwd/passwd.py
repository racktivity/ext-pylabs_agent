__author__ = 'incubaid'
__tags__ = 'agent', 'passwd'
__priority__= 1

def main(q, i, params, tags):
    q.logger.log("agent passwd params:%s tags:%s"%(params,tags))
    
    agentname, password, domain, xmppserver = params['params']
    
    if not 'agent' in q.config.list():
        raise RuntimeError("No Agent configuration found...")
    agentInifile = q.config.getInifile('agent')
    agentConfig = agentInifile.getFileAsDict()
    targetAccountList = filter(lambda accountDetailes: accountDetailes[1].get('agentname') == agentname and accountDetailes[1].get('domain') == domain and accountDetailes[1].get('server') == xmppserver,  
                                      map(lambda accountSectionName: (accountSectionName, agentConfig.get(accountSectionName)), filter(lambda sectionname: sectionname.startswith('account_') and sectionname != 'main', agentConfig.keys())))
    if not targetAccountList:
        raise RuntimeError("No local account found for agentname: %s domain: %s and server: %s"%(agentname, domain, xmppserver))
    accountName, accountDetails = targetAccountList[0]
    oldPassword = accountDetails.get('password')
    
    agentJID = '%s@%s'%(agentname, domain)
    try:
        xmppclient = q.clients.xmpp.getConnection(agentJID, oldPassword, xmppserver)
        xmppclient.changePassword(password)
    except Exception, ex:
        raise RuntimeError('Failed to change password for agent %s on server %s. Reason: %s'%(agentJID, xmppserver, ex))
    else:
        q.logger.log('Password for agent %s on server %s changed Successfully'%(agentJID, xmppserver), 5)
        params['returncode'] = 0
        params['returnvalue'] = 'Password for agent %s on server %s changed Successfully'%(agentJID, xmppserver)
    agentInifile.setParam(accountName, 'password', password)
    q.logger.log('Restarting the agent process...', 5)
    q.kernel.agent.stop()
    q.kernel.agent.start()
    

def match(q, i, params, tags):
    return True
