__tags__ = 'qpackages'
__priority__ = 2


def match(q, i, params, tags):
    return params['subcmd'] == 'install'

def main(q, i, params, tags):
    q.logger.log("qpackages install params:%s tags:%s"%(params,tags))
    params["returnmessage"] = 'Successfully executed command qpackages install' 
    params["returncode"] = 0



