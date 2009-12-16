__tags__ = "agent"
__priority__ = 2


def match(q, i, params, tags):
    q.logger.log("agent passwd newpassword:%s tags:%s"%(params,tags))
    return params['subcmd'] == 'passwd'

def main(q, i, params, tags):
    q.logger.log("agent passwd newpassword:%s tags:%s"%(params,tags))
    params["returnmessage"] = 'Successfully executed command agent passwd'
    params["returncode"] = 0


