__tags__ = 'system'
__priority__ = 2


def match(q, i, params, tags):
    return params['subcmd'] == 'setpasswd'

def main(q, i, params, tags):
    q.logger.log("system setpasswd params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])
    
    args = params['params']
    username, password = args
    
    q.logger.log('username:%s, password:%s'%tuple(args))
    cmd = 'net user %s %s'%(username, password) if q.platform.isWindows() else 'echo %s | passwd --stdin %s'%(password, username)
    output = q.system.process.executeAsync(cmd, argsInCommand = True)
    output.wait()
    resultMessage = ('Password for user %s changed Successfully'%username) if output.returncode == 0 else ''.join(output.stderr.readlines())
    returnCode = output.returncode        
    
    params["returnmessage"] = resultMessage 
    params["returncode"] = returnCode



