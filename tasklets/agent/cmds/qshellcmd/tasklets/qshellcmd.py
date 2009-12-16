__tags__ = 'qshellcmd'
__priority__ = 1


def match(q, i, params, tags):
    return True

def main(q, i, params, tags):
    q.logger.log("qshellcmd params:%s tags:%s"%(params,tags))
    params["returnmessage"] = 'Successfully executed command qshellcmd' 
    params["returncode"] = 0



