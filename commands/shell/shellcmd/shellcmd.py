__author__ = 'incubaid'
__tags__ = 'shellcmd'
__priority__= 1

def main(q, i, params, tags):
    q.logger.log("shellcmd params:%s tags:%s"%(params,tags))

    script = '&&'.join(';'.join(params['params']).split('\n'))
    captureOutput = '-no' not in params['options']
    params['returncode'], returnValue = q.system.process.execute(script)
    if captureOutput:
        params['returnvalue'] = returnValue
        

def match(q, i, params, tags):
    return True
