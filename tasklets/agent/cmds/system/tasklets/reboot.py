__tags__ = 'system'
__priority__ = 1


def match(q, i, params, tags):
    return params['subcmd'] == 'reboot'

def main(q, i, params, tags):
    q.logger.log("system reboot params:%s tags:%s"%(params,tags))
    params["returnmessage"] = 'Successfully executed command system reboot' 
    params["returncode"] = 0



