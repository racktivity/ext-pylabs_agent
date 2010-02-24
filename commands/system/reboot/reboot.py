__author__ = 'incubaid'
__tags__ = 'system', 'reboot'
__priority__= 1

def main(q, i, params, tags):
    q.logger.log("system reboot params:%s tags:%s"%(params,tags))
    cmd = 'shutdown /r' if q.platform.isWindows() else 'reboot'
    params['returncode'], params['returnvalue'] = q.system.process.execute(cmd)

def match(q, i, params, tags):
    return True
