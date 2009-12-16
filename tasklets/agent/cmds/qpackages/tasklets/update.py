__tags__ = 'qpackages'
__priority__ = 4


def match(q, i, params, tags):
    return params['subcmd'] == 'update'

def main(q, i, params, tags):
    q.logger.log("qpackages update params:%s tags:%s"%(params,tags))
    params["returnmessage"] = 'Successfully executed command qpackages update' 
    params["returncode"] = 0



