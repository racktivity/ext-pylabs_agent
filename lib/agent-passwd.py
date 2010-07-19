from pymonkey.InitBaseCore import q
from agent import Agent
import sys
import time
import os
q.application.appname = 'agentpassword'
q.application.start()

agent = Agent()
agent.start()
agent.modifyPassword(sys.argv[1], sys.argv[2])
agent.stop()
os._exit(0)
