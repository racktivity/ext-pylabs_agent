__author__      = 'incubaid'
__tags__        = 'remotesupport', 'open'
__priority__    = 1

import time, re


def match(q, i, params, tags):
    return True

def main(q, i, params, tags):
    
    def get_domain_from_agentid(agentid):
      
        domain = None 
        
        p = r'agent([0-9])+_(?P<domain>[a-zA-Z0-9_\-]+)@agent.sso.daas.com'
        r = re.match(p, agentid) 
        
        if r: 
            d = r.groupdict()
            if 'domain' in d.keys():
                domain = d['domain'].replace('_', '.')
            
        return domain
            
        
    
    q.logger.log("remotesupport params:%s tags:%s" % (params,tags))
    
    # Defaults 
    TIMEOUT = 10
    
    # Get parameters
    args        = params['params'] 
    agentid     = params['agentid']
    domainname  = get_domain_from_agentid(agentid)
    
    server, login, password, serverport, remotehost = args
    
    # Check if we're not connected yet
    pidfile = q.system.fs.joinPaths(q.dirs.pidDir, 'remotesupport.pid')
    if q.system.fs.isFile(pidfile) and q.system.process.isPidAlive(int(q.system.fs.fileGetContents(pidfile))):
        raise RuntimeError('Remote support already in use')
    
    # Cleanup
    cfg_path = q.system.fs.joinPaths(q.dirs.cfgDir, 'remotesupport.cfg')
    q.system.fs.remove(cfg_path, True)
    
    
    
    # Launch remote support connector
    python_bin = q.system.fs.joinPaths(q.dirs.binDir, 'python')
    script = q.system.fs.joinPaths(q.dirs.appDir, 'agent','lib', 'remotesupportconnector.py')
    
    command = '%s %s %s %s %s %s %s %s %s'%(python_bin, script, server, login, password, serverport, remotehost, domainname, agentid )    
    pid = q.system.process.runDaemon(command)
    

    timeout = TIMEOUT
    while timeout > 0 and not q.system.process.isPidAlive(pid):
        time.sleep(1)
        timeout -= 1

    if not timeout:
        raise RuntimeError('Failed to start remote support connector in %d seconds' % TIMEOUT)

    q.system.fs.writeFile(pidfile, str(pid))
    
    # Read cfg if available
    timeout = TIMEOUT
    # Wait until connection should be up
    time.sleep(timeout)
    while timeout > 0 and not q.system.fs.exists(cfg_path):
        time.sleep(1)
        timeout -= 1
    
    if not timeout:
        raise RuntimeError('Failed to read proxy info in %d seconds' % TIMEOUT*2)
    
    cfg = q.tools.inifile.open(cfg_path)
        
    params['returncode'] = 0
    params['returnvalue'] = cfg.getFileAsDict()
