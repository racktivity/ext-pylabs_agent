__tags__ = 'agent'
__priority__ = 1


import xmpp

#DEFAULT_USERNAME = 'defagent'
#DEFAULT_PASSWORD = 'defagent'

def match(q, i, params, tags):
    q.logger.log("agent register xmppServers:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])
    return params['subcmd'] == 'register'

def main(q, i, params, tags):
    q.logger.log("agent register params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])

    q.logger.log("Executing agent register", tags='tasknr:%s'%params['tasknr'])
    args = params['params']
    if 'main' in i.config.agent.list():
            config = i.config.agent.getConfig('main')
            username = config['agentguid']
            password = config['password']
    else:
        raise RuntimeError('No configuration found for agent')
    q.logger.log("xmppservers: %s"%args, tags='tasknr:%s'%params['tasknr'])
    for xmppServer in args:
        client = xmpp.Client(xmppServer)
        if not client.connect():
            q.logger.log("Failed to connect to xmppserver %s"%xmppServer, tags = 'tasknr:%s'%params['tasknr'])
            continue
        iq = xmpp.Iq("get", xmpp.NS_REGISTER)
        try:
            client.send(iq)
        except:
            q.logger.log("Failed to send register request to xmppserver %s"%xmppServer, tags = "tasknr:%s"%params["tasknr"])
            continue
        iq = xmpp.Iq("set", xmpp.NS_REGISTER)
        iq.T.query.NT.username = username
        iq.T.query.NT.password = password
        try:
            client.send(iq)
        except:
            q.logger.log("Failed to register agent with xmmpserver %s"%xmppServer, tags = "tasknr:%s"%params["tasknr"])
            

    params["returnmessage"] = 'Successfully executed command agent register :)'
    params["returncode"] = 0


