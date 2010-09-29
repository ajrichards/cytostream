#!/usr/bin/python  

''' 
call to initialize cytostream  
A. Richards    
adam.richards@stat.duke.edu  
'''

import sys
if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use('Agg') 

#import matplotlib
#matplotlib.use("Qt4Agg")



from cytostream.qtlib import Main

Main()
