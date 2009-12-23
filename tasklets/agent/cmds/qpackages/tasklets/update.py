__tags__ = 'qpackages'
__priority__ = 4


def match(q, i, params, tags):
    return params['subcmd'] == 'update'

def main(q, i, params, tags):
    q.logger.log("qpackages update params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])
    
    script = '\n'.join(['q.qpackages.updateQPackageList()', 'q.qpackages.updateAllQPackages()'])
    params['executeAsyncQshellCommand'](script, params)
    params["returnmessage"] = 'Successfully executed command qpackages update' 
    params["returncode"] = 0



