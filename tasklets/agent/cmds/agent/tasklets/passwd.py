__tags__ = "agent"
__priority__ = 2



def match(q, i, params, tags):
    q.logger.log("agent passwd newpassword:%s tags:%s"%(params,tags))
    return params['subcmd'] == 'passwd'

def main(q, i, params, tags):
    q.logger.log("agent passwd params:%s tags:%s"%(params,tags))
    
    args = params['params']
    q.logger.log("newpassword: %s"%args[0], tags='tasknr:%s'%params['tasknr'])
    
    if 'main' in i.config.agent.list():
            config = i.config.agent.getConfig('main')
            username = config['agentname']
            domain = config['domain']
            password = config['password']
    else:
        raise RuntimeError('No configuration found for agent')
    
    config['password'] = args[0]
    
    xmppserverList = i.config.agent.list()
    if 'main' in xmppserverList:
        xmppserverList.pop(xmppserverList.index('main'))
    for xmppserver in xmppserverList:
        agentJID = '%s@%s'%(username, domain)
        try:
            xmppclient = q.clients.xmpp.getConnection(agentJID, password, xmppserver)
            xmppclient.changePassword(args[0])
        except Exception, ex:
            q.logger.log('Failed to change password for agent %s on server %s. Reason: %s'%(agentJID, xmppserver, ex), 5)
        q.logger.log('Password for agent %s on server changed Successfully'%(agentJID, xmppserver), 5)
    
    i.config.agent.configure('main', config)
#    the following call hangs the application server
#    q.manage.applicationserver.restart()
    
    params["returnmessage"] = 'Successfully executed command agent passwd'
    params["returncode"] = 0


