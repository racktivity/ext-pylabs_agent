__tags__ = 'task'
__priority__ = 2

import signal

def match(q, i, params, tags):
    return params['subcmd'] == 'kill'

def main(q, i, params, tags):
    q.logger.log("task kill params:%s tags:%s"%(params,tags), tags = 'tasknr:%s'%params['tasknr'], level=6)
    
    q.logger.log("tasknr: %s"%params['tasknr'])
    args = params['params']
    if params['killTask'](args[0]):
        q.logger.log('Successfully executed command task kill for tasknr %s'%args[0], tags = 'tasknr:%s'%params['tasknr'])
    else:
        q.logger.log('Could not execute the command task kill for tasknr %s'%args[0], tags = 'tasknr:%s'%params['tasknr'])
    params["returnmessage"] = '' 
    params["returncode"] = 0