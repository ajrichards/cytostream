import sys,os,re
import numpy as np

import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from matplotlib.nxutils import points_inside_poly
from cytostream.tools import rgb_to_hex, get_cmap_blues, get_file_sample_stats, get_all_colors
from fcm.graphics import bilinear_interpolate
'''
the functions here use CytostreamPlotter.py as a parent

'''

def draw_scatter(ax,events,indicesFG,indicesBG,index1,index2,labels,markerSize,highlight,colorList):
    """
    draw the events in a scatte plot based on background and foreground

    """

    myCmap = mpl.cm.gist_heat # spectral hot, gist_heat jet

    ms = markerSize
    if str(labels) == "None":
        dataX,dataY = (events[:,index1],events[:,index2])
        ax.scatter([dataX],[dataY],color='blue',s=markerSize,edgecolor='none')
        return

    ## plot the background events
    if len(indicesBG) > 0:
        clrs = colorList[indicesBG]
        dataX,dataY = (events[indicesBG,index1],events[indicesBG,index2])
        ax.scatter([dataX],[dataY],c='gray',s=ms,edgecolor='none',alpha=0.5)
        ms = markerSize + 3

    ## plot the foreground events
    if len(indicesFG) > 0:
        clrs = colorList[indicesFG]
        dataX,dataY = (events[indicesFG,index1],events[indicesFG,index2])
        ax.scatter([dataX],[dataY],c=clrs,s=ms,edgecolor='none',cmap=myCmap)


def draw_labels(ax,events,indicesFG,indicesBG,index1,index2,labels,markerSize,highlight,centroids,numSubplots):
    """
    draw the labels based on sample centroids in a plot based on foreground and background

    """

    if str(labels) == "None":
        return


    if centroids == None:
        print "WARNING: BasePlotters: cannot specify highlight without centroids"
        return

    def draw_centroid(l,index1,index2,labelSize):
        
        labelColor = "#0000D0"#"#C0C0C0"
        alphaVal = 0.6
        xPos = centroids[str(int(l))][index1]
        yPos = centroids[str(int(l))][index2]

        #if xPos < 0 or yPos <0:
        #    continue
         
        ax.text(xPos, yPos, '%s%s'%(prefix,l),color='#FFFF00',fontsize=labelSize,
                ha="center", va="center",
                bbox = dict(boxstyle="round",facecolor=labelColor,alpha=alphaVal)
                )
        
    ## variables
    prefix = ''
    uniqueLabels = np.unique(labels)

    if numSubplots in [1]:
        labelSize = 7
    elif numSubplots in [2]:
        labelSize = 7
    elif numSubplots in [3]:
        labelSize = 6
    elif numSubplots in [4]:
        labelSize = 6
    elif numSubplots in [5,6]:
        labelSize = 5
    elif numSubplots in [7,8,9]:
        labelSize = 5
    elif numSubplots in [10,11,12]:
        labelSize = 5
    elif self.numSubplots in [13,14,15,16]:
        labelSize = 5

    if len(uniqueLabels) > 50:
        labelSize = labelSize - 2
    elif len(uniqueLabels) > 25:
        labelSize = labelSize - 1

    ## handle highlight version
    if centroids[str(int(labels[0]))].size != events.shape[1]:
        print "ERROR: ScatterPlotter.py -- centroids not same shape as events"

    if str(highlight) != "None" and len(highlight) > 0:
        for l in highlight:
            draw_centroid(l,index1,index2,labelSize)
    else:
        for l in uniqueLabels:
            draw_centroid(l,index1,index2,labelSize)        

def finalize_draw(ax,events,index1,index2,fileChannels,buff,fontSize,fontName,forceScale):
    ## handle data edge buffers     
    bufferX = buff * (events[:,index1].max() - events[:,index1].min())
    bufferY = buff * (events[:,index2].max() - events[:,index2].min())
    ax.set_xlim([events[:,index1].min()-bufferX,events[:,index1].max()+bufferX])
    ax.set_ylim([events[:,index2].min()-bufferY,events[:,index2].max()+bufferY])
    
    ## handle labels and title
    channel1 = fileChannels[index1]
    channel2 = fileChannels[index2]
    ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
    ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

    for t in ax.get_xticklabels():
        t.set_fontsize(fontSize)
        t.set_fontname(fontName)
    
    for t in ax.get_yticklabels():
        t.set_fontsize(fontSize)
        t.set_fontname(fontName)
    
    if forceScale != None:
        xAxLimit,yAxLimit = forceScale
        ax.set_xlim(xAxLimit)
        ax.set_ylim(yAxLimit)
    
    if forceScale == True:
        ax.set_xlim(self.xAxLimit)
        ax.set_ylim(self.yAxLimit)
    
    ## make axes square
    ax.set_aspect(1./ax.get_data_ratio())

def draw_plot(args,parent=None):

    ## handle args
    events=args[0]
    selectedFileName=args[1]
    channel1Ind=args[2]
    channel2Ind=args[3]
    subsample=args[4]
    labels=args[5]
    modelRunID=args[6]
    highlight=args[7]
    log=args[8]
    ax=args[9]
    drawState=args[10]
    numSubplots=args[11]
    forceScale=args[12]
    axesLabels=args[13]
    subplotTitle=args[14]

    ## setup log
    if parent != None:
        log = parent.log.log

    ## other variables
    centroids = None
    buff = 0.02
    markerSize = 1
    masterColorList = get_all_colors()

    if parent != None and channel1Ind != None:
        parent.selectedChannel1=channel1Ind
        parent.channel1Selector.setCurrentIndex(parent.selectedChannel1)
    if parent != None and channel2Ind != None:
        parent.selectedChannel2=channel2Ind
        parent.channel2Selector.setCurrentIndex(parent.selectedChannel2)

    #if events != None:
    #    parent.events=events
    #    parent.selectedFileName=selectedFileName
    #    parent.subsample=subsample
    #    parent.labels=labels
    #    parent.modelRunID = modelRunID
    #    parent.highlight=highlight
    #    parent.log=log

    if numSubplots == None:
        numSubplots = 1


    if parent != None and parent.highlight == "None":
        parent.highlight = None

    ## clear axis
    if parent != None:
        parent.ax.clear()
        parent.ax.grid(parent.grid_cb.isChecked())
    else:
        ax.clear()

    ## declare variables
    if log == None:
        fontName = 'Arial'
        plotType = 'png'
        filterInFocus = None
        fileChannels = ['blah1','blah2','blah3','blah4']
    else:
        fontName = log['font_name']
        plotType = log['plot_type']
        filterInFocus = log['filter_in_focus']
        fileChannels = log['alternate_channel_labels']

    ## specify events and labels
    if parent != None:
        events = parent.events
        labels = parent.labels
        ax = parent.ax
        highlight = parent.highlight

    if type(labels) == type([]):
        labels = np.array(labels)

    ## specify channels
    if parent != None:
        channel1Ind = int(parent.selectedChannel1)
        channel2Ind = int(parent.selectedChannel2)
    
    channel1 = fileChannels[channel1Ind]
    channel2 = fileChannels[channel2Ind]
    
    ## get centroids
    if parent != None and str(labels) != "None":
        plotID, channelsID = parent.pdo.get_ids(parent.selectedFileName,parent.subsample,parent.modelRunID,channel1Ind,channel2Ind)
        centroids = parent.pdo.get_centroids(parent.events,parent.labels,plotID,channelsID)
    elif parent == None and str(labels) != "None":
        centroids,variances,sizes = get_file_sample_stats(events,labels)

    ## error check
    if str(labels) != "None":
        n,d = events.shape
        if n != labels.size:
            print "ERROR: ScatterPlotter.py -- labels and events do not match",n,labels.size
            return None

    ## handle fontSize, labelSize
    if numSubplots in [1]:
        fontSize = 11
    elif numSubplots in [2]:
        fontSize = 10
    elif numSubplots in [3]:
        fontSize = 8
    elif numSubplots in [4]:
        fontSize = 8
    elif numSubplots in [5,6]:
        fontSize = 7
    elif numSubplots in [7,8,9]:
        fontSize = 6
    elif numSubplots in [10,11,12]:
        fontSize = 5
    elif self.numSubplots in [13,14,15,16]:
        fontSize = 4

    ## handle highlighting
    totalPts = len(labels)
    if highlight != None and str(labels) == "None":
        print "ERROR in BasePlotters highlight must have labels too"

    if highlight != None and type(highlight) != type([]):
        print "ERROR: in BasePlotters highlight call must be of type list"
    
    if highlight != None and type(highlight) == type([]) and str(labels) != "None":
        indicesFG = np.array([])
        
        for clustID in highlight:
            if clustID not in labels:
                continue

            indicesFG = np.hstack([indicesFG, np.where(labels==clustID)[0]])

        indicesFG = [int(i) for i in indicesFG]
        indicesBG = list(set(np.arange(totalPts)).difference(set(indicesFG)))

    else:
        indicesFG = np.arange(totalPts)
        indicesBG = []

    ## draw the points
    if str(labels) != None and drawState == 'scatter':
        if max(labels) > len(masterColorList):
            print "WARNING: BasePlotters.draw_plot not enough colors in master color list"
        colorList = masterColorList[labels]
    if str(labels) != None and drawState == 'heat':
        if totalPts >= 9e04:
            bins = 80.0
        elif totalPts >= 8e04:
            bins = 7.0
        elif totalPts >= 7e04:
            bins = 60.0
        elif totalPts >= 6e04:
            bins = 50.0
        elif totalPts >= 5e04:
            bins = 40.0
        elif totalPts >= 4e04:
            bins = 30.0
        elif totalPts >= 3e04:
            bins = 30.0
        elif totalPts >= 2e04:
            bins = 30.0
        elif totalPts >= 1e04:
            bins = 30.0
        else:
            bins = 30.0

        colorList = bilinear_interpolate(events[:,channel1Ind],events[:,channel2Ind],bins=bins)
    else:
       colorList = None

    if type(colorList) == type([]):
        colorList = np.array(colorList)
                                           
    if drawState in ['scatter', 'heat']:
        draw_scatter(ax,events,indicesFG,indicesBG,channel1Ind,channel2Ind,labels,markerSize,highlight,colorList)
        draw_labels(ax,events,indicesFG,indicesBG,channel1Ind,channel2Ind,labels,markerSize,highlight,centroids,numSubplots)
        
        ## handle title and labels
        if parent != None and parent.title_cb.isChecked() == True:
            parent.ax.set_title("%s_%s_%s"%(channel1,channel2,parent.selectedFileName),fontname=fontName,fontsize=fontSize)
        
        if parent != None and parent.axLab_cb.isChecked() == True:
            ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
            ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

        if axesLabels[0] != None:
            ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
        if axesLabels[1] != None:
            ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

        if subplotTitle != None:
            ax.set_title(subplotTitle,fontname=fontName,fontsize=fontSize)

        finalize_draw(ax,events,channel1Ind,channel2Ind,fileChannels,buff,fontSize,fontName,forceScale)

        if parent != None:
            parent.canvas.draw()
    else:
        print "ERROR: BasePlotters: draw state not implemented", drawState
