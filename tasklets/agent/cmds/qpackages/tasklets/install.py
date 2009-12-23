__tags__ = 'qpackages'
__priority__ = 2


def match(q, i, params, tags):
    return params['subcmd'] == 'install'

def main(q, i, params, tags):
    q.logger.log("qpackages install params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])
    
    args = params['params']
    name, version, domain = args[0], None, None
    if len(args) > 1:
        version = args[1]
    if len(args) > 2:
        domain = args[2]
    script = \
"""
res = q.qpackages.qpackageFind(name = '%s', version = %s , domain = %s, state = q.enumerators.QPackageState.SERVER)
if len(res) > 1:raise RuntimeError('More than one package found')
if not res: raise RuntimeError('No Package found')
q.logger.log('QPackage %%s found and will being installed...'%%res[0])
res[0].install()
q.logger.log('QPackage %%s installed Successfully'%%res[0])
"""
    params['executeAsyncQshellCommand'](script%(name, ("'%s'"%version) if version else  'None', ("'%s'"%domain) if domain else  'None'), params)



