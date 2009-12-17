__tags__ = 'qpackages'
__priority__ = 2


def match(q, i, params, tags):
    return params['subcmd'] == 'install'

def main(q, i, params, tags):
    q.logger.log("qpackages install params:%s tags:%s"%(params,tags))
    
    args = params['params']
    q.logger.log("name: %s"%args[0])    
    q.logger.log("version: %s"%args[1])
    q.logger.log("domain: %s"%args[2])        
    
    params["returnmessage"] = 'Successfully executed command qpackages install' 
    params["returncode"] = 0



