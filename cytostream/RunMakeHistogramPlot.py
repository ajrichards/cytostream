#!/usr/bin/python
#

import getopt,sys,os,re
import numpy as np
import matplotlib as mpl
from cytostream import Controller
from cytostream import get_fcs_file_names

## important line to fix popup error in mac osx
if mpl.get_backend() != 'agg':
    mpl.use('agg')

import matplotlib.pyplot as plt
from cytostream import SaveSubplots

try:
    optlist, args = getopt.getopt(sys.argv[1:],'h:f:m:s:c:')
except getopt.GetoptError:
    print getopt.GetoptError

homeDir = None
run = True
for o, a in optlist:
    if o == '-h':
        homeDir = a
    if o == '-f':
        figName = a
    if o == '-c':
        chanInd = int(a)
    if o == '-s':
        subsample = a

if subsample != 'original':
    subsample = int(float(subsample))

## initialze project and fetch data
fileList = get_fcs_file_names(homeDir)
controller = Controller(debug=False)
controller.initialize_project(homeDir,loadExisting=True)
plotsToViewFiles = controller.log.log['plots_to_view_files']
fileName = fileList[int(plotsToViewFiles[0])]
data = controller.get_events(fileName,subsample='1e05')
data = data[:,chanInd]

## prepare figure and plot
fig = plt.figure(figsize=(3,3))
ax = fig.add_subplot(111)
n, bins, patches = plt.hist(data,bins=15,normed=1,facecolor='#333333',alpha=0.75)

## axes and save
ax.set_yticks([])
ax.set_xticks([])
ax.set_title('')
ax.set_ylabel('')
ax.set_xlabel('')
ax.set_frame_on(False)
buff = 0.02
bufferX = buff * (data.max() - data.min())
ax.set_xlim([data.min()-bufferX,data.max()+bufferX])

fig.savefig(figName,transparent=False,dpi=50,bbox_inches='tight')
