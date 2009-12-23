__tags__ = 'system'
__priority__ = 1


def match(q, i, params, tags):
    return params['subcmd'] == 'reboot'

def main(q, i, params, tags):
    q.logger.log("system reboot params:%s tags:%s"%(params,tags), tags = 'tasknr:%s'%params['tasknr'])
    
    cmd = 'shutdown /r' if q.platform.isWindows() else 'reboot'
    output = q.system.process.executeAsync(cmd, argsInCommand = True)
    output.wait()
    params["returnmessage"] = 'Successfully executed command system reboot' if output.returncode == 0 else ''.join(output.stderr.readlines())
    params["returncode"] = output.returncode



