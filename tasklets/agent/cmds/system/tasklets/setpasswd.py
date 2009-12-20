__tags__ = 'system'
__priority__ = 2


def match(q, i, params, tags):
    return params['subcmd'] == 'setpasswd'

def main(q, i, params, tags):
    q.logger.log("system setpasswd params:%s tags:%s"%(params,tags))
    
    args = params['params']
    username, password = args
    
    q.logger.log('username:%s, password:%s'%args)
    
    params["returnmessage"] = 'Successfully executed command system setpasswd' 
    params["returncode"] = 0



