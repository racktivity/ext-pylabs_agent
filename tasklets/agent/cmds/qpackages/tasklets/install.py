__tags__ = 'qpackages'
__priority__ = 2


def match(q, i, params, tags):
    return params['subcmd'] == 'install'

def main(q, i, params, tags):
    q.logger.log("qpackages install params:%s tags:%s"%(params,tags))
    
    args = params['params']
    name, version, domain = args
    q.logger.log("name:%s, version:%s, domain:%s"%args)    
    
    params["returnmessage"] = 'Successfully executed command qpackages install' 
    params["returncode"] = 0



