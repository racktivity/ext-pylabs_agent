__author__ = 'incubaid'
__tags__ = 'process', 'kill'
__priority__= 1

import signal

def main(q, i, params, tags):
    q.logger.log("process kill params:%s tags:%s"%(params,tags))
    
    args = params['params']
    q.system.process.kill(int(args[0]), signal.SIGTERM)    
    q.logger.log('Successfully executed command process kill for process %s'%args[0])
    params["returnvalue"] = '' 
    params["returncode"] = 0

def match(q, i, params, tags):
    return True
