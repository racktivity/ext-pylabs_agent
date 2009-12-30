__tags__ = "agent"
__priority__ = 2


import xmpp 

def match(q, i, params, tags):
    q.logger.log("agent passwd newpassword:%s tags:%s"%(params,tags))
    return params['subcmd'] == 'passwd'

def main(q, i, params, tags):
    q.logger.log("agent passwd params:%s tags:%s"%(params,tags))
    
    args = params['params']
    q.logger.log("newpassword: %s"%args[0], tags='tasknr:%s'%params['tasknr'])
    
    if 'main' in i.config.agent.list():
            config = i.config.agent.getConfig('main')
            username = config['agentguid']
            password = config['password']
            domain = config['xmppserver'] or config['hostname']
    else:
        raise RuntimeError('No configuration found for agent')
    
    config['password'] = args[0]
    
    client = xmpp.Client(domain)
    if not client.connect():
        raise RuntimeError('Failed to connect to the xmppserver %s, check if the server is up and running'%domain)
    
    try:
        client.auth(username, password)
    except Exception, ex:
        raise RuntimeError('Failed to connect to the xmppserver %s with JID %s@%s and password %s'%(domain, username, domain, password))
    
    
    iq = xmpp.Iq('set', xmpp.NS_REGISTER)
    iq.T.query.NT.username = username
    iq.T.query.NT.password = args[0]
    try:
        client.send(iq)
    except Exception, ex:
        raise RuntimeError('Failed to change password for agent with JID %s@%s. Reason: %s'(username, domain, ex.message))
    
    i.config.agent.configure('main', config)
#    the following call hangs the application server
#    q.manage.applicationserver.restart()
    
    params["returnmessage"] = 'Successfully executed command agent passwd'
    params["returncode"] = 0


