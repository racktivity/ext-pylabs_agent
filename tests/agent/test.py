__tags__ = 'test'
__priority__ = 1


def match(q, i, params, tags):
    q.logger.log("Test Tasklet, match,  params:%s tags:%s"%(params,tags))
    return True

def main(q, i, params, tags):
    q.logger.log("Test Tasklet  main, params:%s tags:%s"%(params,tags))

    import time
    params['currentTime'] = time.ctime()
