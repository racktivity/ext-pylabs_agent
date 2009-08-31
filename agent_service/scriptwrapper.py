import sys
sys.path.append('/opt/qbase3/apps/applicationServer/services/')

from pymonkey import q
from agent_service.logtarget import AgentLogTarget

import sys, traceback, time, yaml

# Read yamled version of the script and the params from stdin
yaml_input = sys.stdin.read()
input = yaml.load(yaml_input)
script = input['script']
params = input['params']

q.logger.addLogTarget(AgentLogTarget())
errormessage = None
try:
    # Run the script using the params
    code = compile(script,'<string>','exec')
    local_ns = {'params':params, 'q':q} 
    global_ns = {}
    exec(code, global_ns, local_ns)
except:
    errormessage = traceback.format_exc()
    
# Construct the return message
returnobject = {"params":params}
if errormessage:
    returnobject["errormessage"] = errormessage
    
# Print the yamled version of the returnobject
print
print "---"
print yaml.dump(returnobject)

sys.exit(0)
