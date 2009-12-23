__tags__ = 'process'
__priority__ = 1


def match(q, i, params, tags):    
    return params['subcmd'] == 'hardkill'

def main(q, i, params, tags):
    q.logger.log("process hardkill params:%s tags:%s"%(params,tags))
    
    q.logger.log("tasknr: %s"%params['tasknr'])
    
    args = params['params']
    #by default the signal is singal.SIGKILL
    q.system.process.kill(int(args[0]))    
    
    params["returnmessage"] = 'Successfully executed command process hardkill for process %s'%args[0] 
    params["returncode"] = 0



