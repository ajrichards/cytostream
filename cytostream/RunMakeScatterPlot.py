#!/usr/bin/python
#
# to run an example
# python RunMakeFigures.py -p Demo -i 0 -j 1 -f 3FITC_4PE_004.fcs -h ./projects/Demo
#

import getopt,sys,os,re
import numpy as np

## important line to fix popup error in mac osx
import matplotlib
matplotlib.use('Agg')
from cytostream import Model, Logger
from cytostream.tools import get_all_colors, fetch_plotting_events, get_file_sample_stats
import matplotlib.pyplot as plt

## parse inputs
def bad_input():
    print "\nERROR: incorrect args"
    print sys.argv[0] + "-p projectID -i channel1 -j channel2 -f selectedFile -a alternateDirectory -s subsample -t modelType -h homeDir"
    print "  projectID    (-p) project name"
    print "  channel1     (-i) channel 1 index"
    print "  channel2     (-j) channel 2 index"
    print "  homeDir      (-h) home directory of current project"
    print "  selectedFile (-f) name of selected file"
    print "  altDir       (-a) alternative directory (optional)"
    print "  subsample    (-s) subsampling number (optional)"
    print "  modelName    (-m) model name"
    print "  modelType    (-t) model type"
    print "\n"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:],'i:j:s:a:p:f:m:t:h:')
except getopt.GetoptError:
    print getopt.GetoptError
    bad_input()

projectID = None
channel1 = None
channel2 = None
selectedFile = None
altDir = None
homeDir = None
modelType = None
modelRunID = None
subsample = "original"
run = True
for o, a in optlist:
    if o == '-i':
        channel1 = int(a)
    if o == '-j':
        channel2 = int(a)
    if o == '-f':
        selectedFile = a
    if o == '-a':
        altDir = a
    if o == '-p':
        projectID = a
    if o == '-s':
        subsample = a
    if o == '-m':
        modelRunID = a
    if o == '-t':
        modelType = a
    if o == '-h':
        homeDir = a

def make_scatter_plot(model,log,selectedFile,channel1Ind,channel2Ind,subsample='original',labels=None,buff=0.02,altDir=None,modelLog=None,centroids=None):

    ## declare variables
    markerSize = int(log.log['scatter_marker_size'])
    fontName = log.log['font_name']
    fontSize = log.log['font_size']
    filterInFocus = log.log['filter_in_focus']
    plotType = log.log['plot_type']
    alphaVal = 0.5

    ## make sure subsampling is that of model run
    if modelLog != None:
        subsample = modelLog['subsample']

    ## prepare figure
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111)
    colors = get_all_colors()

    ## specify channels
    fileChannels = log.log['alternate_channel_labels']
    index1 = int(channel1Ind)
    index2 = int(channel2Ind)
    channel1 = fileChannels[index1]
    channel2 = fileChannels[index2]

    ## get events
    events,labels = fetch_plotting_events(selectedFile,model,log,subsample,labels=labels)

    if labels != None:
        n,d = events.shape
        if n != labels.size:
            print "ERROR: RunMakeScatterPlot.py -- labels and events do not match",n,labels.size
            return None

    ## handle centroids
    if labels != None:
        centroids,variances,sizes = get_file_sample_stats(events,labels)

    ## make plot
    totalPoints = 0
    if labels == None:
        ax.scatter([events[:,index1]],[events[:,index2]],color='blue',s=markerSize)
    else:
        if type(np.array([])) != type(labels):
            labels = np.array(labels)

        numLabels = np.unique(labels).size
        maxLabel = np.max(labels)
        cmp = model.get_n_color_colorbar(maxLabel+1)

        for l in np.sort(np.unique(labels)):
            clusterColor = colors[l]

            x = events[:,index1][np.where(labels==l)[0]]
            y = events[:,index2][np.where(labels==l)[0]]
            
            totalPoints+=x.size

            if x.size == 0:
                continue
            ax.scatter(x,y,color=clusterColor,s=markerSize)

            ## handle centroids if present    
            prefix = ''
            alphaVal = 0.8

            if centroids != None:
                if centroids[str(int(l))].size != events.shape[1]:
                    print "ERROR: ScatterPlotter.py -- centroids not same shape as events"

                xPos = centroids[str(int(l))][index1]
                yPos = centroids[str(int(l))][index2]

                if xPos < 0 or yPos <0:
                    continue

                if clusterColor in ['#FFFFAA','y','#33FF77']:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=fontSize,
                                 ha="center", va="center",
                                 bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                 )
                else:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=fontSize,
                                 ha="center", va="center",
                                 bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                 )

    ## handle data edge buffers                                                    
    bufferX = buff * (events[:,index1].max() - events[:,index1].min())
    bufferY = buff * (events[:,index2].max() - events[:,index2].min())
    ax.set_xlim([events[:,index1].min()-bufferX,events[:,index1].max()+bufferX])
    ax.set_ylim([events[:,index2].min()-bufferY,events[:,index2].max()+bufferY])

    ## save file
    fileName = selectedFile
    ax.set_title("%s_%s_%s"%(channel1,channel2,fileName),fontname=fontName,fontsize=fontSize)
    ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
    ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)
    
    if altDir == None:
        fileName = os.path.join(model.homeDir,'figs',"%s_%s_%s.%s"%(selectedFile,channel1,channel2,plotType))
        fig.savefig(fileName,transparent=False,dpi=50)
    else:
        fileName = os.path.join(altDir,"%s_%s_%s.%s"%(selectedFile,channel1,channel2,plotType))
        fig.savefig(fileName,transparent=False,dpi=50)


## error checking
if altDir == 'None':
    altDir = None
if homeDir == 'None':
    homeDir = None
if modelRunID == 'None':
    modelRunID = None
    statModel,statModelClasses = None,None

if altDir == None and homeDir == None:
    bad_input()
    run = False
    print "WARNING: RunMakeFigures failed errorchecking"
 
if projectID == None or channel1 == None or channel2 == None or selectedFile == None:
    bad_input()
    run = False
    print "WARNING: RunMakeFigures failed errorchecking"

if os.path.isdir(homeDir) == False:
    print "ERROR: homedir does not exist -- bad project name", projectID, homeDir
    run = False

if altDir != None and os.path.isdir(altDir) == False:
    print "ERROR: specified alternative dir does not exist\n", altDir
    run = False

if run == True:
    ## initialize a logger and a model to get specified files and channels     
    log = Logger()
    log.initialize(projectID,homeDir,load=True)
    model = Model()
    model.initialize(projectID,homeDir)

    if modelRunID == None:
        make_scatter_plot(model,log,selectedFile,channel1,channel2,subsample=subsample,altDir=altDir)
    else:
        statModel, statModelClasses = model.load_model_results_pickle(selectedFile,modelRunID,modelType=modelType)
        modelLog = model.load_model_results_log(selectedFile,modelRunID)
        if modelType in ['components','modes']:
            pass
        else:
            statModel,statModelClasses = None, None
            labels = None

        make_scatter_plot(model,log,selectedFile,channel1,channel2,labels=statModelClasses,modelLog=modelLog,subsample=subsample,altDir=altDir)
