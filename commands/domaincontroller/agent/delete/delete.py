__author__ = 'incubaid'
__tags__ = 'agent', 'delete'
__priority__= 1

def main(q, i, params, tags):
    agentname, domain = params['params']
    try:
        q.manage.servers.ejabberd.userDelete(agentname, domain)
        params['returncode'] = 0
        params['returnvalue'] = 'agent %s deleted successfully'%agentname
    except:
        params['returncode'] = -1
        params['returnvalue'] = 'failed to delete agent %s'%agentname

def match(q, i, params, tags):
    return True
