__author__ = 'incubaid'
__tags__ = 'domaincontroller', 'register'
__priority__= 1

def main(q, i, params, tags):
    q.logger.log("domaincontroller register agent with params %s"%params, 5)
    
    agentname, password, domain = params['params']
    
    isRegistered = q.manage.servers.ejabberd.isRegistered(agentname, domain)
    if isRegistered:
        params['returncode'] = -1
        params['returnvalue'] = 'agent with jid %s@%s already registered'%(agentname, domain)
    else:
        q.manage.servers.ejabberd.userAdd(agentname, password, domain)
        params['returncode'] = 0
        params['returnvalue'] = 'agent %s@%s registered successfully'%(agentname, domain)
    
def match(q, i, params, tags):
    return True
