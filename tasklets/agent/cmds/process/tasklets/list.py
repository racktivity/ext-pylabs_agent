__tags__ = 'process'
__priority__ = 3


def match(q, i, params, tags):
    return params['subcmd'] == 'list'

def main(q, i, params, tags):
    q.logger.log("process list params:%s tags:%s"%(params,tags))
    params["returnmessage"] = 'Successfully executed command process list' 
    params["returncode"] = 0



