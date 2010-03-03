__author__ = 'incubaid'
__tags__ = 'portforward', 'close'
__priority__= 1
import signal

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
    serverport, localDestination, portOnDestination, loginPasswordServer = args
    q.logger.log("serverport:%s localDestination:%s portOnDestination:%s loginPasswordServer:%s"%(serverport, localDestination, portOnDestination, loginPasswordServer))
    login, password, server = _processLoginInfo(loginPasswordServer)
    connection = q.remote.system.connect(server, login, password)
    q.logger.log('login: %s, password: %s, server: %s'%(login, password, server))
    local = 0 if '-R' in params['options'] else 1
    pidFileName = '%s_%s.pid'%('local' if local else 'remote', serverport)
    pidFilePath = q.system.fs.joinPaths(q.dirs.pidDir, pidFileName)
    if not q.system.fs.isFile(pidFilePath):
        raise RuntimeError('Port %s is not open'%serverport)
    pid = int(q.system.fs.fileGetContents(pidFilePath))
    params['returncode'] = 0
    params['returnvalue'] = 'Port %s closed successfully'%serverport
    if local:
        q.system.process.kill(pid, signal.SIGTERM)
    else:
        params['returncode'], output = connection.process.killProcess(pid)
        if not output:
            output = 'Port %s closed successfully'%serverport
        params['returnvalue'] = output
    q.system.fs.removeFile(pidFilePath)
        
