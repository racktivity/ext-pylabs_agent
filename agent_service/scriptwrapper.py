import sys
from pymonkey.InitBaseCore import q,i
print '!!!'

sys.path.append(q.system.fs.joinPaths(q.dirs.appDir, 'applicationserver','services'))
from agent_service.logtarget import AgentLogTarget

import traceback, time, yaml
import base64

##temporary fix SSOBF-217
import os
os.umask(022)
#########################
# Read yamled version of the script and the params from stdin
yaml_input = sys.stdin.read()
input = yaml.load(yaml_input)
script = input['script']
params = input['params']
#script = base64.decodestring(script)
q.logger.logTargetAdd(AgentLogTarget(maxVerbosityLevel=int(params['maxloglevel'])))
q.logger.log('DEBUG: @SCRIPTWRAPPER: maxloglevel:%s'%(params['maxloglevel']))
errormessage = None

try:
    # Run the script using the params
    code = compile(script,'<string>','exec')
    local_ns = {'params':params, 'q':q, 'i':i}
    global_ns = local_ns

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
