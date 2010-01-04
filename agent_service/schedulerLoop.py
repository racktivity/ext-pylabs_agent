import time        
import xmlrpclib
schedulerPath = params['scheduler_param_schedulerPath']
groupName = params['scheduler_param_groupName']
ip = params['scheduler_param_ip']
port = int(params['scheduler_param_port'])
groupParamKeys = filter(lambda key: not key.startswith('scheduler_param_'), params)
params = dict(zip(groupParamKeys, [params[key] for key in groupParamKeys]))
taskletEngine = q.getTaskletEngine(q.system.fs.joinPaths(schedulerPath, groupName))        
proxy = xmlrpclib.ServerProxy('http://%s:%d/'%(ip, port))        

while True:
    taskletEngine.execute(params,tags=(groupName,))
    # send updated params to our scheduler through xmlrpc
    proxy.agent_service.setSchedulerParams(groupName, params)
    if 'break' in params:
        params['break'] = False 
    time.sleep(10)
