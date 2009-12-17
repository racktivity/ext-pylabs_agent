__tags__ = 'portforward'
__priority__ = 1


def match(q, i, params, tags):
    q.logger.log("portforward params:%s tags:%s"%(params,tags))
    return True

def main(q, i, params, tags):
    q.logger.log("portforward params:%s tags:%s"%(params,tags))
    
    args = params['params']
    q.logger.log("serverport: %s"%args[0])
    q.logger.log("localdestination: %s"%args[1])
    q.logger.log("portondestination: %s"%args[2])
    q.logger.log("$login:$passwd@$sshServerInPubDC: %s"%args[3])
    
    params["returnmessage"] = 'Successfully executed command portforward' 
    params["returncode"] = 0



