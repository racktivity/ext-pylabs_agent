__tags__ = 'qshellcmd'
__priority__ = 1


def match(q, i, params, tags):
    return True

def main(q, i, params, tags):
    q.logger.log("qshellcmd params:%s tags:%s"%(params,tags))
    
    captureOutput = '-no' not in params['options']
    logLevelOption = filter(lambda x : x[:2]== '-l', params['options'])    
    script = '\n'.join(params['params'])
    q.logger.log("DEBUG: before executing the qshell command(s)")
    if logLevelOption:
        params['executeAsyncQshellCommand'](script, params, captureOutput, int(logLevelOption[0][2:]))
    else:
        params['executeAsyncQshellCommand'](script, params, captureOutput)