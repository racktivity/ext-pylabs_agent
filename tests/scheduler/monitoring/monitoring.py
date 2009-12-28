__tags__ = 'monitoring'
__priority__ = 1


def match(q, i, params, tags):
    q.logger.log("Monitoring Tasklet, match,  params:%s tags:%s"%(params,tags))
    return True

def main(q, i, params, tags):
    q.logger.log("Monitoring Tasklet  main, params:%s tags:%s"%(params,tags))

    import time
    params['currentTime'] = time.ctime()