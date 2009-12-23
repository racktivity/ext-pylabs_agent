__tags__ = 'process'
__priority__ = 3


def match(q, i, params, tags):
    return params['subcmd'] == 'list'

def main(q, i, params, tags):
    q.logger.log("process list params:%s tags:%s"%(params,tags))
    cmd = 'tasklist' if q.platform.isWindows() else 'ps -awx'
    output = q.system.process.executeAsync(cmd, argsInCommand=True)
    output.wait()
    
    outputMessage = ''.join(output.stdout.readlines())
    
    params["returnmessage"] = outputMessage if output.returncode == 0 else ''.join(output.stderr.readlines())
    params["returncode"] = output.returncode
    


