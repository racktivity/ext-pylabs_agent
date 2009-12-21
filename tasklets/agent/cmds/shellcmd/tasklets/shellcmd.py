__tags__ = 'shellcmd'
__priority__ = 1


def match(q, i, params, tags):
    return True

def main(q, i, params, tags):
    q.logger.log("shellcmd params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])

    cmd = ';'.join('\n'.join(params['params']).split('\n'))
    output = q.system.process.executeAsync(cmd,argsInCommand=True)
    while output.poll() == None:
        line = output.stdout.readline()
        if line:
            q.logger.log(line, tags='tasknr:%s'%params['tasknr'])

    params["returnmessage"] = 'Successfully executed command shellcmd :)' if output.returncode == 0 else '\n'.join(output.stderr.readlines())
    params["returncode"] = output.returncode



