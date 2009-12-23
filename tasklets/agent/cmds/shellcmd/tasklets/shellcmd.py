__tags__ = 'shellcmd'
__priority__ = 1


def match(q, i, params, tags):
    return True

def main(q, i, params, tags):
    q.logger.log("shellcmd params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])

    script = '&&'.join(';'.join(params['params']).split('\n'))
    captureOutput = '-no' not in params['options']
    params['executeAsyncShellCommand'](script, params, captureOutput)
    



