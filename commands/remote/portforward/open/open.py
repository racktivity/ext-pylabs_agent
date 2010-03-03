__author__ = 'incubaid'
__tags__ = 'portforward', 'open'
__priority__= 1

import time


def match(q, i, params, tags):
    q.logger.log("portforward params:%s tags:%s"%(params,tags))
    return True

def _processLoginInfo(loginPasswordServer):
    login, rest = loginPasswordServer.split(':')
    password, server = rest.split('@')
    return login, password, server

def main(q, i, params, tags):
    q.logger.log("portforward params:%s tags:%s"%(params,tags))
    timeout = 5
    args = params['params']
    serverport, localDestination, portOnDestination, loginPasswordServer = args
    q.logger.log("serverport:%s localDestination:%s portOnDestination:%s loginPasswordServer:%s"%(serverport, localDestination, portOnDestination, loginPasswordServer))
    login, password, server = _processLoginInfo(loginPasswordServer)
    q.logger.log('login: %s, password: %s, server: %s'%(login, password, server))
#    connection = q.remote.system.connect(server, login, password)
    #user 0/1 to indicates local/remote portforwarding, using int(local) in the runner DONT CHANGE HERE WITHOUT CHANGING IN THE RUNNER
    local = 1
    if '-R' in params['options']:
#        connection.portforward.forwardRemotePort(int(serverport), localDestination, int(portOnDestination))
        local = 0

#    else:
#        connection.portforward.forwardLocalPort(int(serverport), localDestination, int(portOnDestination))
    newPidFileName = '%s_%s.pid'%('local' if local else 'remote', serverport)
    newPidFilePath = q.system.fs.joinPaths(q.dirs.pidDir, newPidFileName)
    if q.system.fs.isFile(newPidFilePath):
        raise RuntimeError('Port %s already in use'%serverport)
    python_bin = q.system.fs.joinPaths(q.dirs.binDir, 'python')
    runnerScriptPath = q.system.fs.joinPaths(q.dirs.appDir, 'agent','lib', 'portforwardrunner.py')
    pidFilePath = q.system.fs.joinPaths(q.dirs.pidDir, '%s_portforward.pid'%params['tasknumber'])
    command = '%s %s start %s %s %s %s %s %s %s %s'%(python_bin, runnerScriptPath, pidFilePath, local, server, login, password, serverport, localDestination, portOnDestination)
    q.system.process.execute(command)
    pidExists = False
    while timeout:
        if q.system.fs.isFile(pidFilePath):
            pidExists = True
            break
        time.sleep(1)
        timeout -= 1
    if not pidExists:
        raise RuntimeError('Failed to start portforward daemon. Reason cannot find pid file in %s seconds'%timeout)
    pid = int(q.system.fs.fileGetContents(pidFilePath))
    q.system.fs.writeFile(newPidFilePath, str(pid))
    params['returncode'] = 0
    params['returnvalue'] = 'Successfully open port'
