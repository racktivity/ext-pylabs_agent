__author__ = 'incubaid'
__tags__ = 'portforward', 'open'
__priority__= 1

fScriptMain = \
"""
connection  = q.remote.system.connect('%s', '%s' , '%s')
%s
"""

rScript = \
"""
connection.portforward.forwardRemotePort(%d, '%s', %d)
"""

lScript = \
"""
connection.portforward.forwardLocalPort(%d, '%s', %d)
"""

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
    q.logger.log('login: %s, password: %s, server: %s'%(login, password, server))
    if '-R' in params['options']:
        script = fScriptMain%(server, login, password, rScript%(int(serverport), localDestination, int(portOnDestination)))
    else:
        script = fScriptMain%(server, login, password, lScript%(int(serverport), localDestination, int(portOnDestination)))
    code = compile(script,'<string>','exec')
    local_ns = {'params':params, 'q':q, 'i':i}
    global_ns = local_ns
    exec(code, global_ns, local_ns)

def match(q, i, params, tags):
    return True
