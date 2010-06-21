__author__ = 'incubaid'
__tags__ = 'remotesupport', 'close'
__priority__= 1
import signal
import time

def match(q, i, params, tags):
    q.logger.log("portforward params:%s tags:%s"%(params,tags))
    return True

def main(q, i, params, tags):
    
    # Constants
    TIMEOUT = 10
    
    # Check if we can/have to execute this action
    pidfile = q.system.fs.joinPaths(q.dirs.pidDir, 'remotesupport.pid')
    pid = int(q.system.fs.fileGetContents(pidfile)) if q.system.fs.isFile(pidfile) else None
    
    if not (pid and q.system.process.isPidAlive(pid)): 
        raise RuntimeError('Remote support is not enabled')
    
    # Try to stop the remote connection
    q.system.process.kill(pid, signal.SIGTERM)
    
    timeout = TIMEOUT
    
    while timeout:
        if not q.system.process.isPidAlive(pid):
            break
        time.sleep(1)
        timeout -= 1
    
    if not timeout:
        q.logger.log('Failed to stop the remote support connection in %s seconds, trying to kill the process abruptly '% TIMEOUT)
        q.system.process.kill(pid, signal.SIGKILL)
        
    isalive = q.system.process.isPidAlive(pid)
    
    params['returncode'] = 0 if not isalive else -1
    params['returnvalue'] = 'Remote support connection closed successfully' if not isalive else 'Failed to close remote support connection'
    
    if not isalive:
        q.system.fs.removeFile(pidfile)
        
