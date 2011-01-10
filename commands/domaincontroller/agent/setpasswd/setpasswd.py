__author__ = 'incubaid'
__tags__ = 'domaincontroller', 'setpasswd'
__priority__= 1

def main(q, i, params, tags):

    q.logger.log("domaincontroller agent setpasswd with params %s"%params, 5)

    try:
        agentname, password, domain, newpasswd = params['params']
        q.manage.servers.ejabberd.changePassword(agentname, domain, newpasswd)
        params['returncode'] = 0
        params['returnvalue'] = 'Password changed successfully'
    except Exception, ex:
        params['returncode'] = 1
        params['returnvalue'] = 'Failed to change the password of agent %s: %s'% (agentname, ex.message)
 
def match(q, i, params, tags):
    return True
