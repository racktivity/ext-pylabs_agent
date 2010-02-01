__tags__ = 'qshellcmd'
__priority__ = 1


def match(q, i, params, tags):
    return True

def main(q, i, params, tags):
    q.logger.log("qshellcmd params:%s tags:%s"%(params,tags))
    
    captureOutput = '-no' not in params['options']
    logLevelOption = filter(lambda x : x[:2]== '-l', params['options'])
    for option in params['options']:
        if option.startswith('-params'):
            additionalParams = eval(option[7:])
            params.update(additionalParams)
    
            
    script = '\n'.join(params['params'])
    if logLevelOption:
        params['executeAsyncQshellCommand'](script, params, captureOutput, int(logLevelOption[0][2:]))
    else:
        params['executeAsyncQshellCommand'](script, params, captureOutput)