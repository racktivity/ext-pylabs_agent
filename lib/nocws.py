import re
import urllib
from pymonkey import q

class RemoteSupportWSClient(object):
    '''
    Client for Zenith NOC remote support webservices 
    '''
    
    def __init__(self, host, port=80, path='/remoteagentservice', https=False):
        '''
        Initialize webservice client with host and port
        
        @param host:             Host on which we can contact the Remote Support Webservices
        @type host:              string
        
        @param port:             Port on which we can contact the Remote Support Webservices
        @type port:              int
        '''
        
        self._host = host
        self._port = port
        self._path = path
        self._https = https
        
        self._http = q.clients.http.getconnection()
        
    def what_is_my_ip(self):
        '''
        Get the internal IP of the SSH server we are connected to
        
        @return:                 host/ip of the connected SSH server
        @rtype:                  string
        '''
        
        service = 'tfr_wpwhatsmyip.asp'
        
        result = self._call_ws(service, 'GET')
    
        # Parse result
        p = r'<sshsvrip>(?P<host>[a-zA-Z0-9\.\-]+)</sshsvrip>'
        r = re.match(p, result) 
            
        if r: 
            d = r.groupdict()
            if 'host' in d.keys():
                host = d['host']
                
        return host
    
    def add_tunnel_info(self, domainname, agentid, remotesship, remotesshport, localip, localport):
        '''
        Notify NOC we have setup a tunnel
        
        @param domainname:       Zenith support domain of the connecting environment
        @type domainname:        string
        
        @param agentid:          JID of the agent which setup the tunnel
        @type agentid:           string
        
        @param remotesship:      IP of the SSH host the tunnel is connected to
        @type remotesship:       string
        
        @param remotesshport:    Remote port where tunnel is connected to
        @type remotesshport:     int
        
        @param localip:          IP of client which is forwarded
        @type localip:           string
        
        @param localport:        Local port which is forwarded
        @type localport:         int
        
        @return:                 True if successfull
        @rtype:                  bool
        '''
        
        return self._update_tunnel_info('ADD', domainname, agentid, remotesship, remotesshport, localip, localport)
        
    def remove_tunnel_info(self, domainname, agentid, remotesship, remotesshport, localip, localport):
        '''
        Notify NOC we have removed a tunnel
        
        @param domainname:       Zenith support domain of the connected environment
        @type domainname:        string
        
        @param agentid:          JID of the agent which setup the tunnel
        @type agentid:           string
        
        @param remotesship:      IP of the SSH host the tunnel is connected to
        @type remotesship:       string
        
        @param remotesshport:    Remote port where tunnel is connected to
        @type remotesshport:     int
        
        @param localip:          IP of client which is forwarded
        @type localip:           string
        
        @param localport:        Local port which is forwarded
        @type localport:         int
        
        @return:                 True if successfull
        @rtype:                  bool
        '''
        
        return self._update_tunnel_info('DELETE', domainname, agentid, remotesship, remotesshport, localip, localport)
        
    def _update_tunnel_info(self, action, domainname, agentid, remotesship, remotesshport, localip, localport):
        '''
        Notify NOC we have updated a tunnel
        
        @param domainname:       Zenith support domain of the connecting environment
        @type domainname:        string
        
        @param agentid:          JID of the agent which setup the tunnel
        @type agentid:           string
        
        @param remotesship:      IP of the SSH host the tunnel is connected to
        @type remotesship:       string
        
        @param remotesshport:    Remote port where tunnel is connected to
        @type remotesshport:     int
        
        @param localip:          IP of client which is forwarded
        @type localip:           string
        
        @param localport:        Local port which is forwarded
        @type localport:         int
        
        @param action:           Action performed on tunnel (ADD or DELETE)
        @type action:            string
        
        @return:                 True if successfull
        @rtype:                  bool
        '''
        service = 'tfr_wpssosshtunnelinfo.asp'
        
        params = { 
                    'domainname': domainname,
                    'agentid': agentid,
                    'remotesship': remotesship,
                    'remotesshport': remotesshport, 
                    'localip': localip,
                    'localport': localport,
                    'action': action,
                  }
        
        query = {
                 'agentid': agentid,
                }
        
        query.update(params)
    
        result = self._call_ws(service, method='GET', query=query)
        
        if not '|' in result:
            raise RuntimeError('Failed to update tunnel info. Result: %s' % result)
        
        code, message = result.split('|')
        
        if code != '1':
            raise RuntimeError('Failed to update tunnel info. Message: %s' % message)
        
        return True
    
    
    def remove_all_tunnels_for_agent(self, domainname, agentid):
        '''
        Remove all tunnel info for an agent
        
        @param domainname:       Zenith support domain of the connected environment
        @type domainname:        string
        
        @param agentid:          JID of the agent which setup the tunnel
        @type agentid:           string
        
        @return:                 True if successfull
        @rtype:                  bool
        '''
        service = 'tfr_wpssoclosetunnel.asp'
        
        params = { 
                    'domainname': domainname,
                 }
        
        query =  {
                    'agentid': agentid,
                 }
        
        query.update(params)
    
        result = self._call_ws(service, method='GET', query=query)
        
        if not '|' in result:
            raise RuntimeError('Failed to remove tunnel info. Result: %s' % result)
        
        code, message = result.split('|')
        
        if code != '1':
            raise RuntimeError('Failed to remove tunnel info. Message: %s' % message)
        
        return True

    def _call_ws(self, service, method='GET', query=None, params=None, headers=None):
        '''
        Calls the specified webservice
        
        @param service:          Name of service to call
        @type service:           string
        
        @param method:           HTTP method to use (GET or POST)
        @type method:            string
        
        @param query:            Dictionary with parameters for the querystring
        @type query:             dict
        
        @param params:           Dictionary with parameters for call (POST only)
        @type params:            dict
        
        @param headers:          Dictionary with additional HTTP headers
        @type headers:           dict
        
        @result:                 Response content of the request
        @rtype:                  string
        '''
        
        uri = self._get_uri(service, query)
        
        result = None
        
        q.logger.log('Calling WS:\nURI: %s\nparams:%s' % (uri, params), 6)
        
        if method == 'POST':
            result = self._http.post(uri, params, headers)
        else:
            result = self._http.get(uri)
            
        q.logger.log( 'WS Result: %s' % result, 6)
        return result
    
    
    def _get_uri(self, service, query=None):
        '''
        Helper method to generate the correct URI to a service
        
        @param service:          Name of the service
        @type service:           string
        
        @return:                 URI of the service
        @rtype:                  string
        '''
        
        def clean_path(path):
            return '/'.join([p for p in path.split('/') if p])
        
        
        uri = 'http%s://%s:%s%s/%s%s' % ('s' if self._https else '', \
                                      self._host,
                                      self._port,
                                      '/' + clean_path(self._path) if self._path else '',
                                      service,
                                      '?' + urllib.urlencode(query) if query else '')
        
        return uri