__tags__ = 'qpackages'
__priority__ = 1


def match(q, i, params, tags):
    return params['subcmd'] == 'emptycache'

def main(q, i, params, tags):
    q.logger.log("qpackages emptycache params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])
    
    script= \
"""
q.system.fs.removeDirTree(q.dirs.packageDir)
q.logger.log('Packages cache has been emptied Successfully')
"""
    params['executeAsyncQshellCommand'](script, params) 



