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
    optlist, args = getopt.getopt(sys.argv[1:],'h:f:m:s:')
except getopt.GetoptError:
    print getopt.GetoptError

homeDir = None
run = True
for o, a in optlist:
    if o == '-h':
        homeDir = a
    if o == '-f':
        figName = a
    if o == '-m':
        mode = a
    if o == '-s':
        subsample = a

if subsample != 'original':
    subsample = int(float(subsample))

if mode == 'qa':
    drawState = 'heat'
else:
    drawState = 'scatter'

ss = SaveSubplots(homeDir,figName,1,figMode=mode,useScale=True,drawState=drawState,hasFrame=False,
                  useSimple=True,figSize=(3,3),subsample=subsample,trimmed=True,dpi=50,drawLabels=False)
