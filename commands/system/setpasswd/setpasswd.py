__author__ = 'incubaid'
__tags__ = 'system', 'setpasswd'
__priority__= 1

def main(q, i, params, tags):
    q.logger.log("system setpasswd params:%s tags:%s"%(params,tags))
    
    args = params['params']
    username, password = args
    
    q.logger.log('username:%s, password:%s'%tuple(args))
    cmd = 'net user %s %s'%(username, password)
    params['returncode'] = 1
    if q.platform.isWindows():
        params['returncode'], params['returnvalue'] = q.system.process.executeAsync(cmd)
    else:
        try:
            import pexpect
        except:
            q.logger.log('Cannot import pexpect module, make sure that the pexpect package is installed on your system')
            params['returnvalue'] = 'Cannot import pexpect module, make sure that the module is installed'
        child = pexpect.spawn('passwd %s'%username)
        if child.expect(['[Oo]ld [Pp]assword', '.current.*password', '.*[Nn]ew.*[Pp]assword']) == 0:
            params['returnvalue'] = 'Failed to change password for user %s'%username
        else:
            child.sendline(password)
            if child.expect(['[Nn]ew [Pp]assword', '[Rr]etype', '[Rr]e-enter']) == 0:
                params['returnvalue'] = 'Failed to change password for user %s'%username
            else:
                child.sendline(password)
                params['returnvalue'] = 'Password for user %s changed Successfully'%username
                params['returncode'] = 0
                
        
    

def match(q, i, params, tags):
    return True
