__author__ = 'incubaid'
__tags__ = 'qshellcmd'
__priority__= 1


def main(q, i, params, tags):
    q.logger.log("qshellcmd params:%s tags:%s"%(params,tags))
    
    captureOutput = '-no' not in params['options']
    logLevelOption = filter(lambda x : x[:2]== '-l', params['options'])
    for option in params['options']:
        if option.startswith('-params'):
            additionalParams = eval(option[7:])
            params.update(additionalParams)
    
            
    script = '\n'.join(params['params'])
    code = compile(script,'<string>','exec')
    local_ns = {'params':params, 'q':q, 'i':i}
    global_ns = local_ns
    exec(code, global_ns, local_ns)

def match(q, i, params, tags):
    return True
