__tags__ = 'portforward'
__priority__ = 1

rforwardScript = \
"""

import socket
import select
import sys
import threading
import paramiko
import SocketServer



def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception, e:
        q.logger.log('Forwarding request to %s:%d failed: %r' % (host, port, e))
        return
    
    q.logger.log('Connected! Tunnel open %r -> %r -> %r' % (chan.origin_addr,
                                                        chan.getpeername(), (host, port)))
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    q.logger.log('Tunnel closed from %r' % (chan.origin_addr,))
    

def reverse_forward_tunnel(server_ip, server_port, remote_host, remote_port, transport):
    transport.request_port_forward(server_ip, server_port)
    while True:
        chan = transport.accept(1000)
        if chan is None:
            continue
        thr = threading.Thread(target=handler, args=(chan, remote_host, remote_port))
        thr.setDaemon(True)
        thr.start()
"""

forwardScript = \
"""

import socket
import select
import sys
import threading
import paramiko
import SocketServer

class ForwardServer (SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True
    
 
class Handler (SocketServer.BaseRequestHandler):
 
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host, self.chain_port),
                                                   self.request.getpeername())
        except Exception, e:
            q.logger.log('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                              self.chain_port,
                                                              repr(e)))
            return
        if chan is None:
            q.logger.log('Incoming request to %s:%d was rejected by the SSH server.' %
                    (self.chain_host, self.chain_port))
            return
 
        q.logger.log('Connected! Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
                                                            chan.getpeername(), (self.chain_host, self.chain_port)))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)
        chan.close()
        self.request.close()
        q.logger.log('Tunnel closed from %r' % (self.request.getpeername(),))
 
 
def forward_tunnel(local_port, remote_host, remote_port, transport):
    # this is a little convoluted, but lets me configure things for the Handler
    # object. (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHander (Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport
    ForwardServer(('', local_port), SubHander).serve_forever()

"""

rScriptMain = \
"""
%s
client = q.clients.ssh.createClient('%s', '%s', '%s', 10)
reverse_forward_tunnel('%s', %d, '%s', %d, client.client.get_transport())
"""

fScriptMain = \
"""
%s
client = q.clients.ssh.createClient('%s', '%s' , '%s' , 10)
forward_tunnel(%d , '%s' , %d , client.client.get_transport())
"""

def match(q, i, params, tags):
    q.logger.log("portforward params:%s tags:%s"%(params,tags))
    return True

def _processLoginInfo(loginPasswordServer):
    login, rest = loginPasswordServer.split(':')
    password, server = rest.split('@')
    return login, password, server

def main(q, i, params, tags):
    q.logger.log("portforward params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])
    
    args = params['params']
    serverport, localDestination, portOnDestination, loginPasswordServer = args
    q.logger.log("serverport:%s localDestination:%s portOnDestination:%s loginPasswordServer:%s"%(serverport, localDestination, portOnDestination, loginPasswordServer), tags='tasknr:%s'%params['tasknr'])
    login, password, server = _processLoginInfo(loginPasswordServer)
    
    if '-R' in params['options']:
        script = rScriptMain%(rforwardScript, server, login, password, server, int(serverport), localDestination, int(portOnDestination))
#        reverse_forward_tunnel(q, server, int(serverport), localDestination, int(portOnDestination), client.client.get_transport())
    else:
        script = fScriptMain%(forwardScript, server, login, password, int(serverport), localDestination, int(portOnDestination))
#        forward_tunnel(q, int(serverport), localDestination, int(portOnDestination), client.client.get_transport())

    params['executeAsyncQshellCommand'](script, params)



