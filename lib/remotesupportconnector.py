# -*- coding: utf-8 -*-
'''
INCUBAID BSD version 2.0 
Copyright � 2010 Incubaid BVBA

All rights reserved. 
 
Redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following 
conditions are met: 
 
* Redistributions of source code must retain the above copyright 
notice, this list of conditions and the following disclaimer. 

* Redistributions in binary form must reproduce the above copyright 
notice, this list of conditions and the following disclaimer in    the documentation and/or other materials provided with the   distribution. 

* Neither the name Incubaid nor the names of other contributors may be used to endorse or promote products derived from this software without specific prior written permission. 
 
THIS SOFTWARE IS PROVIDED BY INCUBAID "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
IN NO EVENT SHALL INCUBAID BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
'''


import sys
import atexit
import signal

from pymonkey.InitBaseCore import q
from nocws import RemoteSupportWSClient



def get_service_host():
    '''
    Figure out the host where services are exposed in the SSO env
    '''
    
    host = '127.0.0.1' # default from local host
    
    if not  'cloudapiconnection' in q.config.list() or not 'main' in q.config.getConfig('cloudapiconnection').keys():
        return host
    
    cfg = q.config.getConfig('cloudapiconnection')['main']
    
    if cfg['server']:
        host = cfg['server']
    
    return host

def get_host_for_service(service, default):
    '''
    Retrieve the correct host for the service
    '''
    # Always forward SSH of local machine
    # Other services on the default host (=dmachine)
    if service == 'ssh':
        return '127.0.0.1'
    else:
        return default
    
def save_proxy_info(proxies):
    '''
    Save current proxy info
    '''
    path = q.system.fs.joinPaths(q.dirs.cfgDir, 'remotesupport.cfg')
    
    cfg = q.tools.inifile.new(path)
    
    for service, proxyinfo in proxies.iteritems():
        cfg.addSection(service)
        
        for k, v in proxyinfo.iteritems():
            cfg.addParam(service, k, v)
            
            
    
        
    
    
    
def disconnect():
    global webservice
    global client
    # Update NOC that tunnels are closed
    # @todo: check if this is sufficient when we stop the remote connection from the agent
    webservice.remove_all_tunnels_for_agent(domainname, agentid)
    client.close()
    
# Read parameters
server, login, password, serverport, remotehost, domainname, agentid = sys.argv[1:]

# Prepare for end of session
atexit.register(disconnect)
# Normal exit when killed
signal.signal(signal.SIGTERM, lambda signum, stack_frame: q.application.stop())

q.application.appname = 'remotesupportconnector'
q.application.start()

services = {
            'ssh': 22, 
            'http': 80, 
            'amf': 8899,
}

proxies = dict.fromkeys(services.keys())  

# G
global client
global webservice

client = q.remote.system.connect(server, login, password, port=int(serverport))

# Get access to the NOC webservices
# This will make the NOC weservices availble on the local machine
# We need it to determine on which SSH host we landed and 
# to notify the NOC we're in

q.logger.log('Forwarding NOC webservice to localhost')
client.portforward.forwardLocalPort(8000, 'remotewebservice', 80, True)

# Get access to the remote support WS
webservice = RemoteSupportWSClient('127.0.0.1', 8000)

# Get the ip of the SSH host on which we landed
ssh_host = webservice.what_is_my_ip()
q.logger.log('IP of SSH host is %s' % ssh_host, 6)

# Get host to forward services for
service_host = get_service_host() 

# Forward all services to ssh host
for service in services.keys():
    # Do not fail in case of 1 failed proxy
    try:
        local_host = get_host_for_service(service, service_host)
        
        proxy_port = client.portforward.forwardRemotePort(0, local_host, services[service], ssh_host, True)
        q.logger.log('Forwarded %s port %s to %s port %s' % (local_host, services[service], ssh_host, proxy_port))
                     
        webservice.add_tunnel_info(domainname, agentid, ssh_host, proxy_port, local_host, services[service])
        
        
        proxies[service] = {'localip': local_host, 
                            'localport': services[service],
                            'remotesship': ssh_host,
                            'remotesshport': proxy_port,                           
                           }
        
    except Exception, ex:
        q.logger.log('Failed to forward service %s! Error: %s' % (service, ex.message), 6)

if len(proxies) == 0:
    raise RuntimeError('Failed to setup remote support connection!')

save_proxy_info(proxies)

# Keep process running!
transport = client._client._transport

# Can't just join the main thread or we won't receive SIGNALS
while transport.isAlive():
    transport.join(60)
    

