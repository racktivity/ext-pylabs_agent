__author__ = 'incubaid'
__tags__ = 'qpackages', 'install'
__priority__= 1

def main(q, i, params, tags):
    args = params['params']
    name, version, domain = args[0], '', ''
    if len(args) > 1:
        version = args[1]
    if len(args) > 2:
        domain = args[2]
    res = q.qp.find(name, version, domain)
    if len(res) > 1:
        raise RuntimeError('More than one package found')
    if not res: 
        raise RuntimeError('No Package found')
    q.logger.log('QPackage %s found and will being installed...'%res[0])
    res[0].install()
    q.logger.log('QPackage %s installed Successfully'%res[0])
    params["returncode"] = 0


def match(q, i, params, tags):
    return True
