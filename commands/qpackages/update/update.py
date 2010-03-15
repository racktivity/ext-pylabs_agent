__author__ = 'incubaid'
__tags__ = 'qpackages', 'update'
__priority__= 1

def main(q, i, params, tags):
    q.logger.log("qpackages update")
    
    args = params['params']
    domain = ''
    if len(args) > 0:
        domain = args[0]
    
    q.qp.updateMetaData(domain)
    # there's no corresponding method for updating the qpackages in non-interactive mode
    #i.qp.updateAll()
    for p in q.qp.getInstalledPackages():
        p.install()

    params["returncode"] = 0

def match(q, i, params, tags):
    return True
