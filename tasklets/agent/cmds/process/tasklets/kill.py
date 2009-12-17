__tags__ = 'process'
__priority__ = 2


def match(q, i, params, tags):
    return params['subcmd'] == 'kill'

def main(q, i, params, tags):
    q.logger.log("process kill params:%s tags:%s"%(params,tags))
    
    q.logger.log("tasknr: %s"%params['tasknr'])    
    
    params["returnmessage"] = 'Successfully executed command process kill' 
    params["returncode"] = 0



