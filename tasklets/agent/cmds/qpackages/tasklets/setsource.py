__tags__ = 'qpackages'
__priority__ = 3


def match(q, i, params, tags):
    return params['subcmd'] == 'setsource'

def main(q, i, params, tags):
    q.logger.log("qpackages setsource params:%s tags:%s"%(params,tags))
    
    args = params['params']
    q.logger.log("source: %s"%args[0])  
    
    params["returnmessage"] = 'Successfully executed command qpackages setsource' 
    params["returncode"] = 0



