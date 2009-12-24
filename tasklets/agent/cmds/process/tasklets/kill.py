__tags__ = 'process'
__priority__ = 2

import signal

def match(q, i, params, tags):
    return params['subcmd'] == 'kill'

def main(q, i, params, tags):
    q.logger.log("process kill params:%s tags:%s"%(params,tags), tags = 'tasknr:%s'%params['tasknr'], level=6)
    
    q.logger.log("tasknr: %s"%params['tasknr'])
    args = params['params']
    q.system.process.kill(int(args[0]), signal.SIGTERM)    
    q.logger.log('Successfully executed command process kill for process %s'%args[0], tags = 'tasknr:%s'%params['tasknr'])
    params["returnmessage"] = '' 
    params["returncode"] = 0



