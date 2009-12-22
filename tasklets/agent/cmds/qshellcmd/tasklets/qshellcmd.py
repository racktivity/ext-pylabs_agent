__tags__ = 'qshellcmd'
__priority__ = 1


def match(q, i, params, tags):
    return True

def main(q, i, params, tags):
    q.logger.log("qshellcmd params:%s tags:%s"%(params,tags))
    
    script = '\n'.join(params['params'])
    q.logger.log("DEBUG: before executing the qshell command(s)")
    params['executeAsyncQshellCommand'](script, params)