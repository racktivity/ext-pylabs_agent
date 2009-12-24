__tags__ = 'process'
__priority__ = 3


def match(q, i, params, tags):
    return params['subcmd'] == 'list'

def main(q, i, params, tags):
    q.logger.log("process list params:%s tags:%s"%(params,tags), tags = 'tasknr:%s'%params['tasknr'])
    script = 'tasklist' if q.platform.isWindows() else 'ps -awx'
    params['executeAsyncShellCommand'](script, params)

