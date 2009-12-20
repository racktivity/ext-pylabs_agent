__tags__ = 'agent'
__priority__ = 1


def match(q, i, params, tags):
    q.logger.log("agent register xmppServers:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])
    return params['subcmd'] == 'register'

def main(q, i, params, tags):
    q.logger.log("agent register params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])

    q.logger.log("Executing agent register", tags='tasknr:%s'%params['tasknr'])
    args = params['params']
    q.logger.log("xmppservers: %s"%args, tags='tasknr:%s'%params['tasknr'])

    params["returnmessage"] = 'Successfully executed command agent register :)'
    params["returncode"] = 0


