#!/usr/bin/python
#

import getopt,sys,os,re
import numpy as np
import matplotlib as mpl

## important line to fix popup error in mac osx
if mpl.get_backend() != 'agg':
    mpl.use('agg')

from cytostream import SaveSubplots

try:
    optlist, args = getopt.getopt(sys.argv[1:],'h:')
except getopt.GetoptError:
    print getopt.GetoptError

homeDir = None
run = True
for o, a in optlist:
    if o == '-h':
        homeDir = a

ss = SaveSubplots(homeDir,figName,numSubplots,figMode=mode,forceScale=False,
                  forceSimple=True,drawState='heat',figSize=(2,2))
