__tags__ = 'portforward'
__priority__ = 1


def match(q, i, params, tags):
    q.logger.log("portforward params:%s tags:%s"%(params,tags))
    return True

def main(q, i, params, tags):
    q.logger.log("portforward params:%s tags:%s"%(params,tags))
    
    args = params['params']
    serverport, localDestination, portOnDestination, loginPasswordServer = args
    q.logger.log("serverport:%s localDestination:%s portOnDestination:%s loginPasswordServer:%s"%args)
    
    params["returnmessage"] = 'Successfully executed command portforward' 
    params["returncode"] = 0



