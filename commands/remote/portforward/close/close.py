__author__ = 'incubaid'
__tags__ = 'portforward', 'close'
__priority__= 1
import signal
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
    
    args = params['params']
    hasTimeout = filter(lambda element: element.startswith('-timeout'), params['options'])
    if hasTimeout:
        _timeout = float(hasTimeout[0][len('-timeout')+1:].strip())
    else:
        _timeout = 5
    timeout = _timeout
    serverport, localDestination, portOnDestination, loginPasswordServer = args
    q.logger.log("serverport:%s localDestination:%s portOnDestination:%s loginPasswordServer:%s"%(serverport, localDestination, portOnDestination, loginPasswordServer))
    login, password, server = _processLoginInfo(loginPasswordServer)
    connection = q.remote.system.connect(server, login, password)
    q.logger.log('login: %s, password: %s, server: %s'%(login, password, server))
    local = 0 if '-R' in params['options'] else 1
    pidFileName = '%s_%s.pid'%('local' if local else 'remote', serverport)
    pidFilePath = q.system.fs.joinPaths(q.dirs.pidDir, pidFileName)
    pid = int(q.system.fs.fileGetContents(pidFilePath)) if q.system.fs.isFile(pidFilePath) else None
    if not (pid and q.system.process.isPidAlive(pid)): # it means if not pid or not ispidalive
        raise RuntimeError('Port %s is not open'%serverport)
    q.system.process.kill(pid, signal.SIGTERM)
    while timeout:
        if not q.system.process.isPidAlive(pid):
            break
        time.sleep(1)
        timeout -= 1
    
    if not timeout:
        q.logger.log('Failed to stop the portforward in %s seconds, trying to kill the process abruptly '%_timeout)
        q.system.process.kill(pid, signal.SIGKILL)
    isAlive = q.system.process.isPidAlive(pid)
    params['returncode'] = 0 if not isAlive else -1
    params['returnvalue'] = 'Port %s closed successfully'%serverport if not isAlive else 'Failed to close port %s'%serverport
    if not isAlive:
        q.system.fs.removeFile(pidFilePath)
        
