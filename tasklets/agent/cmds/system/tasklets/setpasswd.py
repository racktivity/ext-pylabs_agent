__tags__ = 'system'
__priority__ = 2


def match(q, i, params, tags):
    return params['subcmd'] == 'setpasswd'

def main(q, i, params, tags):
    q.logger.log("system setpasswd params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])
    
    args = params['params']
    username, password = args
    
    q.logger.log('username:%s, password:%s'%tuple(args))
    cmd = 'net user %s %s'%(username, password)
    returnCode = 1
    if q.platform.isWindows():
        output = q.system.process.executeAsync(cmd, argsInCommand = True)
        output.wait()
        resultMessage = ('Password for user %s changed Successfully'%username) if output.returncode == 0 else ''.join(output.stderr.readlines())
        returnCode = output.returncode
    else:
        try:
            import pexpect
        except:
            q.logger.log('Cannot import pexpect module, make sure that the module is installed', tags='tasknr:%s'%params['tasknr'])
            resultMessage = 'Cannot import pexpect module, make sure that the module is installed'
        child = pexpect.spawn('passwd %s'%username)
        if child.expect(['[Oo]ld [Pp]assword', '.current.*password', '.*[Nn]ew.*[Pp]assword']) == 0:
            resultMessage = 'Failed to change password for user %s'%username
        else:
            child.sendline(password)
            if child.expect(['[Nn]ew [Pp]assword', '[Rr]etype', '[Rr]e-enter']) == 0:
                resultMessage = 'Failed to change password for user %s'%username
            else:
                child.sendline(password)
                resultMessage = 'Password for user %s changed Successfully'%username
                returnCode = 0
                
        
    
    params["returnmessage"] = resultMessage 
    params["returncode"] = returnCode



