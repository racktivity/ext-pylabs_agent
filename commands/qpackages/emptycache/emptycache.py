__author__ = 'incubaid'
__tags__ = 'qpackages', 'emptycache'
__priority__= 1

def main(q, i, params, tags):
    
    q.system.fs.removeDirTree( q.system.fs.joinPaths(q.dirs.varDir, 'qpackages4'))
    q.logger.log('Packages cache has been emptied Successfully')    
    

def match(q, i, params, tags):
    return True
