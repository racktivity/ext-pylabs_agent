__tags__ = 'breaktest'
__priority__ = 1


def match(q, i, params, tags):
    q.logger.log("BreakTest priority2 , match,  params:%s tags:%s"%(params,tags))
    if 'break' in params:
        return not params['break']
    return True

def main(q, i, params, tags):
    q.logger.log("BreakTest priority2, main, params:%s tags:%s"%(params,tags))
    if 'counter' not in params:
        params['counter'] = 0

    params['counter'] = int(params['counter']) + 30