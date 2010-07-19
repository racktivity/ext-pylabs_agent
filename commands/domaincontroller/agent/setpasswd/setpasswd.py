__author__ = 'incubaid'
__tags__ = 'domaincontroller', 'setpasswd'
__priority__= 1

def main(q, i, params, tags):
    agentname, password, domain, newpasswd = params['params']
    try:
        q.manage.servers.ejabberd.changePassword(agentname, domain, password)
        params['returncode'] = 0
        params['returnvalue'] = 'Password changed successfully'
    except:
        params['returncode'] = 1
        params['returnvalue'] = 'Failed to change the password of agent %s'%agentname

def match(q, i, params, tags):
    return True
