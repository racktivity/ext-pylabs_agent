__tags__ = 'agent'
__priority__ = 1


def match(q, i, params, tags):
    q.logger.log("agent register xmppServers:%s tags:%s"%(params,tags))
    return params['subcmd'] == 'register'

def main(q, i, params, tags):
    q.logger.log("agent register xmppServers:%s tags:%s"%(params,tags))
    params["returnmessage"] = 'Successfully executed command agent register' 
    params["returncode"] = 0



