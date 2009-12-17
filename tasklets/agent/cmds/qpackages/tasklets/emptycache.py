__tags__ = 'qpackages'
__priority__ = 1


def match(q, i, params, tags):
    return params['subcmd'] == 'emptycache'

def main(q, i, params, tags):
    q.logger.log("qpackages emptycache params:%s tags:%s"%(params,tags))
    
    params["returnmessage"] = 'Successfully executed command qpackages emptycache' 
    params["returncode"] = 0



