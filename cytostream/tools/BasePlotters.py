import sys,os,re
import numpy as np
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from matplotlib.nxutils import points_inside_poly
from matplotlib.ticker import ScalarFormatter
from cytostream.tools import rgb_to_hex, get_cmap_blues, get_file_sample_stats, get_all_colors
from cytostream.tools import set_logicle_transformed_ticks, set_scatter_ticks, set_log_transformed_ticks
from fcm.graphics import bilinear_interpolate

'''
the functions here use CytostreamPlotter.py as a parent

'''

def draw_scatter(ax,events,indicesFG,indicesBG,index1,index2,labels,markerSize,highlight,colorList,
                 drawState='heat',borderEvents=[],nonBorderEvents=[]):
    """
    draw the events in a scatte plot based on background and foreground

    """

    myCmap = mpl.cm.gist_heat  #  spectral hot, gist_heat jet

    ms = markerSize
    if str(labels) == "None" and drawState in ['scatter']:
        dataX,dataY = (events[:,index1],events[:,index2])
        ax.scatter([dataX],[dataY],color='blue',s=markerSize,edgecolor='none')
        return

    ## plot the background events
    if len(indicesBG) > 0:
        dataX,dataY = (events[indicesBG,index1],events[indicesBG,index2])
        ax.scatter([dataX],[dataY],c='gray',s=ms,edgecolor='none',alpha=0.8)
        ms = markerSize

    ## plot the foreground events
    if len(indicesFG) > 0:
        if drawState == 'heat':
            dataX,dataY = (events[indicesFG,index1],events[indicesFG,index2])
            borderEventsX1 = np.where(dataX == 0)[0]
            borderEventsX2 = np.where(dataY == dataX.max())[0]
            borderEventsY1 = np.where(dataY == 0)[0]
            borderEventsY2 = np.where(dataY == dataY.max())[0]
            borderEventsX = np.hstack([borderEventsX1,borderEventsX2])
            borderEventsY = np.hstack([borderEventsY1,borderEventsY2])
            borderEvents = np.hstack([borderEventsX,borderEventsY])
            
            nonBorderEvents = np.array(list(set(range(len(indicesFG))).difference(set(borderEvents))))
            colorList = bilinear_interpolate(dataX[nonBorderEvents],dataY[nonBorderEvents],bins=colorList)

            ## plot events
            ax.scatter([dataX[nonBorderEvents]],[dataY[nonBorderEvents]],c=colorList,s=1,edgecolor='none',cmap=myCmap)
            if borderEvents.size > 0:
                ax.scatter([dataX[borderEvents]],[dataY[borderEvents]],c='k',s=1,edgecolor='none')
        
def draw_labels(ax,events,indicesFG,indicesBG,index1,index2,labels,markerSize,highlight,centroids,numSubplots):
    """
    draw the labels based on sample centroids in a plot based on foreground and background

    """

    colorList = get_all_colors()

    if str(labels) == "None":
        return

    if centroids == None:
        print "WARNING: BasePlotters: cannot specify highlight without centroids"
        return

    def draw_centroid(l,index1,index2,labelSize):
        
        labelColor = "#0000D0"#"#C0C0C0"
        alphaVal = 0.6

        if centroids.has_key(str(int(l))) == False:
            return

        ##################
        if len(labels) != events.shape[0]:
            print "WARNING: BasePlotters.py -- problem drawing cluster centroids"

        #clusterInds = np.where(labels==l)[0]
        #xPos = events[clusterInds,index1].mean()
        #yPos = events[clusterInds,index2].mean()
        #################

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
    elif numSubplots in [13,14,15,16]:
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

def finalize_draw(ax,events,index1,index2,fileChannels,buff,fontSize,fontName,useSimple=False,axesOff=False):
    ## handle data edge buffers     
    bufferX = buff * (events[:,index1].max() - events[:,index1].min())
    bufferY = buff * (events[:,index2].max() - events[:,index2].min())
    ax.set_xlim([events[:,index1].min()-bufferX,events[:,index1].max()+bufferX])
    ax.set_ylim([events[:,index2].min()-bufferY,events[:,index2].max()+bufferY])

    ## axes formatters
    formatter = ScalarFormatter(useMathText=True) 
    formatter.set_scientific(True)
    formatter.set_powerlimits((-3,3))
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter) 

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
    
    ## for an axesless vesion
    if axesOff == True:
        ax.set_yticks([])
        ax.set_xticks([])

    ## for a simple version
    if useSimple == True:
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_title('')
        ax.set_ylabel('')
        ax.set_xlabel('')
        #ax.set_xlim([0,700])
        #ax.set_ylim([0,820])

    ## make axes square
    ax.set_aspect(1./ax.get_data_ratio())

def draw_plot(args,parent=None,axesOff=False):
    ''' 
    draw_plot takes args to create a plot 
    can be entirely independent of classes however a parent
    or a CytostreamPlotter instance may be provided 

    args[0] = ax                       [required]  matplotlib axes
    args[1] = events                   [required]  np.array (N,D)
    args[2] = channel1Index            [required]  int
    args[3] = channel2Index            [required]  int
    args[4] = subsample                [required]  float | 'original'
    args[5] = labels                   [optional]  np.array (N,1)
    args[6] = subplotHighlight         [optional]  None|clusterID (str(int))
    args[7] = logger                   [optional]  Logger instance
    args[8] = drawState                [optional]  scatter | heat | contour
    args[9] = numSubplots              [optional]  int 1-16
    args[10] = axesLabels              [optional]  None | (xAxisLabel,yAxisLabel)
    args[11] = plotTitle               [optional]  None | str
    args[12] = showNoise               [optional]  True | False
    args[13] = useSimple               [optional]  False | True

    '''

    ## handle args
    ax           = args[0]
    events       = args[1]
    channel1Ind  = args[2]
    channel2Ind  = args[3]
    subsample    = args[4]
    labels       = args[5]
    highlight    = args[6]
    log          = args[7]
    drawState    = args[8]
    numSubplots  = args[9]
    axesLabels   = args[10]
    plotTitle    = args[11]
    showNoise    = args[12]
    useSimple    = args[13]

    ## force drawState to heat if necessary
    if labels == None:
        drawState = 'heat'

    ## other variables
    centroids = None
    buff = 0.02
    markerSize = 1
    masterColorList = get_all_colors()

    if parent != None and channel1Ind != None:
        widet.selectedChannel1=channel1Ind
        parent.channel1Selector.setCurrentIndex(parent.selectedChannel1)
    if parent != None and channel2Ind != None:
        parent.selectedChannel2=channel2Ind
        parent.channel2Selector.setCurrentIndex(parent.selectedChannel2)

    if numSubplots == None:
        numSubplots = 1

    ## highlight
    if parent != None and str(parent.highlight) == "None":
        parent.highlight = None
    elif parent != None and str(parent.highlight) != "None":
        highlight = [parent.highlight]

    ## clear axis
    ax.clear()    
    if parent != None:
        parent.ax.grid(parent.grid_cb.isChecked())

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
    elif numSubplots in [13,14,15,16]:
        fontSize = 4

    ## handle highlighting
    totalPts,totalDims = events.shape

    if str(highlight) != "None" and str(labels) == "None":
        print "ERROR in BasePlotters highlight must have labels too"

    if str(highlight) != "None" and type(highlight) != type([]):
        print "ERROR: in BasePlotters highlight call must be of type list"
    
    if str(highlight) != "None" and type(highlight) == type([]) and str(labels) != "None":
        
        indicesFG = np.array([])
        if type(highlight) != type([]):
            highlight = [highlight]
        if type(highlight[0]) == type([]):
            highlight = highlight[0]

        for clustID in highlight:
            if int(clustID) not in labels:
                continue

            indicesFG = np.hstack([indicesFG, np.where(labels==int(clustID))[0]])

        indicesFG = [int(i) for i in indicesFG]
        indicesBG = list(set(np.arange(totalPts)).difference(set(indicesFG)))
    else:
        indicesFG = np.arange(totalPts)
        indicesBG = []

    ## draw the points
    if str(labels) != "None" and drawState == 'scatter':
        if max(labels) > len(masterColorList):
            print "WARNING: BasePlotters.draw_plot not enough colors in master color list"
        colorList = masterColorList[labels]

    elif  drawState == 'heat':
        if totalPts >= 9e04:
            bins = 120.0
        elif totalPts >= 8e04:
            bins = 120.0
        elif totalPts >= 7e04:
            bins = 120.0
        elif totalPts >= 6e04:
            bins = 100.0
        elif totalPts >= 5e04:
            bins = 100.0
        elif totalPts >= 4e04:
            bins = 80.0
        elif totalPts >= 3e04:
            bins = 70.0
        elif totalPts >= 2e04:
            bins = 60.0
        elif totalPts >= 1e04:
            bins = 60.0
        else:
            bins = 50.0

        colorList=bins
    else:
       colorList = None

    if type(colorList) == type([]):
        colorList = np.array(colorList)
   
    if drawState in ['scatter', 'heat']:
        draw_scatter(ax,events,indicesFG,indicesBG,channel1Ind,channel2Ind,labels,markerSize,highlight,colorList,
                     drawState=drawState)
        
        if str(labels) != "None":
            draw_labels(ax,events,indicesFG,indicesBG,channel1Ind,channel2Ind,labels,markerSize,highlight,centroids,numSubplots)
        
        ## handle title and labels
        if parent != None and parent.title_cb.isChecked() == True:
            parent.ax.set_title("%s_%s_%s"%(channel1,channel2,parent.selectedFileName),fontname=fontName,fontsize=fontSize)
        
        if parent != None and parent.axLab_cb.isChecked() == True:
            ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
            ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

        if axesLabels != None:
            if axesLabels[0] != None:
                ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
            if axesLabels[1] != None:
                ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

        if plotTitle != None:
            ax.set_title(subplotTitle,fontname=fontName,fontsize=fontSize)

        finalize_draw(ax,events,channel1Ind,channel2Ind,fileChannels,buff,fontSize,fontName,useSimple,axesOff)

        if parent != None:
            parent.canvas.draw()
    else:
        print "ERROR: BasePlotters: draw state not implemented", drawState

def create_cytokine_subplot(nga,ax,fileName,index1,index2,filterID,fThreshold,bins=120,fontSize=7,fontName='arial',
                            yLabel='default',xLabel='default',title=None,yLim=None,xLim=None,
                            useColor=True,transform=('logicle','x')):
    buff = 0.02
    if useColor == True:
        myCmap = mpl.cm.gist_heat
        scatterColor = 'blue'
        thresholdColor = 'orange'
    else:
        myCmap = mpl.cm.gray
        scatterColor = '#555555'
        thresholdColor = 'k'

    ## load events
    events = nga.get_events(fileName,filterID=filterID)
    dataX,dataY = (events[:,index1],events[:,index2])

    ## get border events
    borderEventsX1 = np.where(dataX == 0)[0]
    borderEventsX2 = np.where(dataY == dataX.max())[0]
    borderEventsY1 = np.where(dataY == 0)[0]
    borderEventsY2 = np.where(dataY == dataY.max())[0]
    borderEventsX = np.hstack([borderEventsX1,borderEventsX2])
    borderEventsY = np.hstack([borderEventsY1,borderEventsY2])
    borderEvents = np.hstack([borderEventsX,borderEventsY])
    nonBorderEvents = np.array(list(set(range(events.shape[0])).difference(set(borderEvents))))
    colorList = bilinear_interpolate(dataX[nonBorderEvents],dataY[nonBorderEvents], bins=bins)

    ## plot events  
    ax.scatter([dataX[nonBorderEvents]],[dataY[nonBorderEvents]],c=colorList,s=1,edgecolor='none',cmap=myCmap)
    ax.scatter([dataX[borderEvents]],[dataY[borderEvents]],c='k',s=1,edgecolor='none')

    fileChannels = nga.get_file_channels()
    if xLabel == 'default':
        ax.set_xlabel(fileChannels[index1],fontname=fontName,fontsize=fontSize) # index1
    elif xLabel != None:
        ax.set_xlabel(xLabel,fontname=fontName,fontsize=fontSize)
    if yLabel == 'default':
        ax.set_ylabel(fileChannels[index2],fontname=fontName,fontsize=fontSize)
    elif yLabel != None:
        ax.set_ylabel(yLabel,fontname=fontName,fontsize=fontSize)

    if title != None:
        ax.set_title(title,fontname=fontName,fontsize=fontSize)

    ## add threshold
    ax.plot(np.array([fThreshold]).repeat(50),np.linspace(dataY.min(),dataY.max(),50),color=thresholdColor,linestyle='-',linewidth=1.0)
    positiveEventInds = np.where(dataX > fThreshold)[0]
    if positiveEventInds.size > 0:
        ax.scatter([dataX[positiveEventInds]],[dataY[positiveEventInds]],c=scatterColor,s=1,edgecolor='none')

    ## axes
    if transform[0] == 'logicle':
        set_logicle_transformed_ticks(ax,axis=transform[1],fontsize=fontSize,fontname=fontName)
        set_scatter_ticks(ax,'y',fontsize=fontSize,fontname=fontName)
    else:
        set_log_transformed_ticks(ax,axis=transform[1],fontsize=fontSize,fontname=fontName)
        set_scatter_ticks(ax,'y',fontsize=fontSize,fontname=fontName)
        
    ax.set_aspect(1./ax.get_data_ratio())
