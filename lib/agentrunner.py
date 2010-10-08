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

from pymonkey.InitBaseCore import q
from agent import Agent

import time

q.application.appname = 'agent'
q.application.start()

SLEEP_INTERVAL = 2

agentVarDir = q.system.fs.joinPaths(q.dirs.varDir, 'agent')
if not q.system.fs.exists(agentVarDir):
    q.system.fs.createDir(agentVarDir)

agent = Agent()
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
 
