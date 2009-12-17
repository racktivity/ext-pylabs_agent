__tags__ = 'process'
__priority__ = 1


def match(q, i, params, tags):    
    return params['subcmd'] == 'hardkill'

def main(q, i, params, tags):
    q.logger.log("process hardkill params:%s tags:%s"%(params,tags))
    
    q.logger.log("tasknr: %s"%params['tasknr'])    
    
    params["returnmessage"] = 'Successfully executed command process hardkill' 
    params["returncode"] = 0



