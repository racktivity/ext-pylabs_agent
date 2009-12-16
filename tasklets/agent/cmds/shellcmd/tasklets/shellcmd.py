__tags__ = 'shellcmd'
__priority__ = 1


def match(q, i, params, tags):
    return True


def main(q, i, params, tags):
    q.logger.log("shellcmd params:%s tags:%s"%(params,tags))
    params["returnmessage"] = 'Successfully executed command shellcmd' 
    params["returncode"] = 0


