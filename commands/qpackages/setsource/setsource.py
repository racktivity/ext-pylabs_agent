__author__ = 'incubaid'
__tags__ = 'qpackages', 'setsource'
__priority__= 1

def main(q, i, params, tags):
    params['result'] = ''

def match(q, i, params, tags):
    args = params['params']
    domain = args[0]
    
    from pymonkey.inifile import IniFile
    f = IniFile(q.system.fs.joinPaths(q.dirs.cfgDir, 'qpackages4', 'sources.cfg'))
    if not domain in  f.getSections():
        raise RuntimeError('domain %s does not exist'% domain)
    
    if len(args) > 1: #mercurialRepo
        f.setParam('pylabs.org', 'metadatafrommercurial', args[1])
    if len(args) > 2: #bundleDownload
        f.setParam('pylabs.org', 'bundledownload', args[2])
    if len(args) > 3: #bundleUpload
        f.setParam('pylabs.org', 'bundleupload', args[3])
    
    
    q.logger.log('QPackages setsource edited sources.cfg successfully')
    params["returncode"] = 0

    
    
