__author__ = 'incubaid'
__tags__ = 'process', 'list'
__priority__= 1

def match(q, i, params, tags):
    return True

def main(q, i, params, tags):
    q.logger.log("process list params:%s tags:%s"%(params,tags))
    command = 'tasklist' if q.platform.isWindows() else 'ps -awx'
    params['returncode'], params['returnvalue'] = q.system.process.execute(command)
