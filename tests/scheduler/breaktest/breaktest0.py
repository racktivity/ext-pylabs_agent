__tags__ = 'breaktest'
__priority__ = 2


def match(q, i, params, tags):
    q.logger.log("BreakTest, match,  params:%s tags:%s"%(params,tags))
    return True

def main(q, i, params, tags):
    q.logger.log("BreakTest, main, params:%s tags:%s"%(params,tags))

    if 'counter' not in params:
        params['counter'] = 0

    params['counter'] = int(params['counter']) + 1
    params['break'] = True
