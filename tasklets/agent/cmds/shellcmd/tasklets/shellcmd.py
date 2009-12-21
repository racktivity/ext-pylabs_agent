__tags__ = 'shellcmd'
__priority__ = 1


def match(q, i, params, tags):
    return True

def main(q, i, params, tags):
    q.logger.log("shellcmd params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])

    cmd = '&&'.join(';'.join(params['params']).split('\n'))
    displayOutput = '-no' not in params['options']
    output = q.system.process.executeAsync(cmd,argsInCommand=True)
#    while output.poll() == None:
#       if displayOutput:
#            line = output.stdout.readline()
#            if line:
#                q.logger.log(line, tags='tasknr:%s'%params['tasknr'])
    output.wait()
    if displayOutput:
        outputMessage = ''.join(output.stdout.readlines())
    else:
        outputMessage = 'Successfully executed command shellcmd :)'

    params["returnmessage"] = outputMessage if output.returncode == 0 else '\n'.join(output.stderr.readlines())
    params["returncode"] = output.returncode




