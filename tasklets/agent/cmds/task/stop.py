__tags__ = 'task'
__priority__ = 2

import signal

def match(q, i, params, tags):
    return params['subcmd'] == 'stop'

def main(q, i, params, tags):
    q.logger.log("task stop params:%s tags:%s"%(params,tags), tags = 'tasknr:%s'%params['tasknr'], level=6)
    
    q.logger.log("tasknr: %s"%params['tasknr'])
    args = params['params']
    if params['stopTask'](args[0]):
        q.logger.log('Successfully executed command task stop for tasknr %s'%args[0], tags = 'tasknr:%s'%params['tasknr'])
    else:
        q.logger.log('Could not execute command task stop for tasknr %s'%args[0], tags = 'tasknr:%s'%params['tasknr'])
    params["returnmessage"] = '' 
    params["returncode"] = 0




