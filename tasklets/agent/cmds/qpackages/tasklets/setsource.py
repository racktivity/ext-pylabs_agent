__tags__ = 'qpackages'
__priority__ = 3


def match(q, i, params, tags):
    return params['subcmd'] == 'setsource'

def main(q, i, params, tags):
    q.logger.log("qpackages setsource params:%s tags:%s"%(params,tags), tags='tasknr:%s'%params['tasknr'])
    
    args = params['params']
    
    script ="""
from pymonkey.inifile import IniFile
inifile = IniFile(q.system.fs.joinPaths(q.dirs.cfgDir, 'qpackageserverlist.cfg'))
fileAsDict = inifile.getFileAsDict()
destItem = 'main' if 'main' in fileAsDict.keys() else fileAsDict.keys()[0]
inifile.setParam(destItem, 'ipaddr', '%s')
inifile.write()
q.logger.log('QPackage server source changed for item %%s to %%s'%%(destItem, '%s'))
"""
    params['executeAsyncQshellCommand'](script%(args[0], args[0]), params) 



