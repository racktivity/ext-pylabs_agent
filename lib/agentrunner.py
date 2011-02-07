#from pymonkey import InitBaseCore
#from pymonkey import q
#
#import sys
#from agent import Agent
#
#import time
#import optparse
#
#from daemon.runner import DaemonRunner
#
#agentVarDir = q.system.fs.joinPaths(q.dirs.varDir, 'agent')
#if not q.system.fs.exists(agentVarDir):
#	q.system.fs.createDir(agentVarDir)
#	
#	
#class AgentRunner(object):
#	pidfile_path = q.system.fs.joinPaths(q.dirs.pidDir, 'agent.pid')
#	stdin = None
#	stdout = None
#	stderr = None
#	pidfile_timeout = 5
#	
#	def run(self):
#		self.agent.start()
#		while True:
#			time.sleep(5)
#
#runner = AgentRunner()
#
#parser = optparse.OptionParser()
#parser.add_option('--use-stdin', dest = 'use_stdin', default = False, action = 'store_true')
#parser.add_option('--use-stdout', dest = 'use_stdout', default = False, action = 'store_true')
#parser.add_option('--use-stderr', dest = 'use_stderr', default = False, action = 'store_true')
#
#options, args = parser.parse_args()
#
#action = args[0]
#
#if options.use_stdin:
#	runner.stdin = sys.stdin
#else:
#	runner.stdin_path = q.system.fs.joinPaths(agentVarDir, 'stdin')
#	if not q.system.fs.exists(runner.stdin_path):
#		q.system.fs.createEmptyFile(runner.stdin_path)
#	
#if options.use_stdout:
#	runner.stdout = sys.stdout
#else:
#	runner.stdout_path = q.system.fs.joinPaths(agentVarDir, 'stdout')
#	
#if options.use_stderr:
#	runner.stderr = sys.stderr
#else:
#	runner.stderr_path = q.system.fs.joinPaths(agentVarDir, 'stderr')
#	
#
#
#if action == 'start':
#	runner.agent = Agent()
#	
#dRunner = DaemonRunner(runner)
#
#actions = {'start': dRunner._start, 'stop': dRunner._stop, 'restart': dRunner._restart}
#
#actions[action]()

import json
import logging
import signal



def write_connection_info(path, info):
    """
    Write JSON serialized connection info to file
    
    Can't use pymonkey as it should work even before pymonkey is loaded 
    """
    logging.log(logging.INFO, 'Writing connection info "%s" to "%s"' % (info, path))
    with open(path, 'w+') as f:
        f.write(json.dumps(info))
        logging.log(logging.INFO, 'Done writing connection info')
        
        
def ignore_signal(signum, frame):
    """
    Write empty connection info
    """
    logging.log(logging.INFO, 'Got signal %s' % signum)
    write_connection_info('/opt/qbase3/var/tmp/agent_connection_info.json', {})
    
signal.signal(signal.SIGRTMIN, ignore_signal)

from pymonkey.InitBaseCore import q
from agent import Agent

import json
import os

import time

q.application.appname = 'agent'
q.application.start()

SLEEP_INTERVAL = 2

agentVarDir = q.system.fs.joinPaths(q.dirs.varDir, 'agent')
if not q.system.fs.exists(agentVarDir):
    q.system.fs.createDir(agentVarDir)

agent = Agent()  

def get_connection_info(signum, frame):
    """
    Write empty connection info
    """
    q.logger.log('Got signal %s' % signum, 2)
       
    try:
        info_path = q.system.fs.joinPaths(q.dirs.tmpDir, 'agent_connection_info.json')
        connection_info = agent.getConnectionInfo()
        q.logger.log('Writing connection info %s to %s' % (connection_info, info_path), 5)
        q.system.fs.writeFile(info_path, json.dumps(connection_info))
    except Exception, ex:
        q.logger.log('Failed writing connection info to %s!' % info_path, 2)

signal.signal(signal.SIGRTMIN, get_connection_info)



agent.start()

accountActive = True
while accountActive:
    accountActive = False
    for jid in agent.accounts.keys() : 
        
        try:
            accountActive = accountActive or not agent.accounts[jid].isShuttingDown()
        except AttributeError, ex:
            # Race condition can recreate the account object while re-connecting
            accountActive = True
        except Exception, ex :
            q.logger.log("%s" % ex)
        
        

    if accountActive:
        time.sleep(SLEEP_INTERVAL)
 
