__author__ = 'incubaid'
__tags__ = 'qpackages', 'emptycache'
__priority__= 1

def main(q, i, params, tags):
    
    # <baseDir>/var/qpackages4/bundles/
    q.system.fs.removeDirTree( q.system.fs.joinPaths(q.dirs.varDir, 'qpackages4', 'bundles'))
    #  cfg/qpackages4/state/
    q.system.fs.removeDirTree( q.system.fs.joinPaths(q.dirs.cfgDir, 'qpackages4', 'state'))    
    q.logger.log('Packages cache has been emptied Successfully')
    params["returncode"] = 0
    
    

def match(q, i, params, tags):
    return True
