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

from pymonkey.InitBaseCore import q
from daemon import DaemonContext
from daemon.runner import DaemonRunner
import lockfile
import sys

class App(object):
        pidfile_path = q.system.fs.joinPaths(q.dirs.pidDir, 'forward.pid')
        stdin_path = q.system.fs.joinPaths(q.dirs.varDir , 'portforward.in')
	if not q.system.fs.isFile(stdin_path):
		q.system.fs.createEmptyFile(stdin_path)
        stdout_path = q.system.fs.joinPaths(q.dirs.varDir , 'portforward.out')
        stderr_path = q.system.fs.joinPaths(q.dirs.varDir , 'portforward.err')
        pidfile_timeout = 5
	stdin = None
	stdout = None
	stdin = None
        def run(self):
                connection = q.remote.system.connect(self.server, self.login, self.password)
		if self.local:
			connection.portforward.forwardLocalPort(int(self.serverport), self.remotehost, int(self.portonhost))
		else:
			connection.portforward.forwardRemotePort(int(self.serverport), self.remotehost, int(self.portonhost))

#def run(local, server,login, password, serverport, remotehost, portonhost):
#    connection = q.remote.system.connect(server, login, password)
#    if local:
#        connection.portforward.forwardLocalPort(int(serverport), remotehost, int(portonhost))
#    else:
#        connection.portforward.forwardRemotePort(int(serverport), remotehost, int(portonhost))

#pidfile, local, server,login, password, serverport, remotehost, portonhost = sys.argv[1:]


#context = DaemonContext()
#context.pidfile = lockfile.FileLock(pidfile)
#context.stdin = open('/tmp/portforward.in', 'r')
#context.stdout = open('/tmp/portforward.out', 'w')
#context.stderr = open('/tmp/portforward.err', 'w')
#with context:
#	run(local, server,login, password, serverport, remotehost, portonhost)

app = App()
action, app.pidfile_path, app.local, app.server, app.login, app.password, app.serverport, app.remotehost, app.portonhost= sys.argv[1:]

dRunner = DaemonRunner(app)
actions = {'start': dRunner._start, 'stop': dRunner._stop, 'restart': dRunner._restart}
actions[action]()
    
