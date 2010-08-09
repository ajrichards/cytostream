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

from cytostream import Main

Main()
