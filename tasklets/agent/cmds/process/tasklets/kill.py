__tags__ = 'process'
__priority__ = 2

import signal

def match(q, i, params, tags):
    return params['subcmd'] == 'kill'

def main(q, i, params, tags):
    q.logger.log("process kill params:%s tags:%s"%(params,tags))
    
    q.logger.log("tasknr: %s"%params['tasknr'])
    args = params['params']
    q.system.process.kill(int(args[0]), signal.SIGTERM)    
    
    params["returnmessage"] = 'Successfully executed command process kill for process %s'%args[0] 
    params["returncode"] = 0



