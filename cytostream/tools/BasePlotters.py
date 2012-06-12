import sys,os,re
import numpy as np
import matplotlib as mpl
import PyQt4.QtGui as QtGui

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from matplotlib.nxutils import points_inside_poly
from matplotlib.ticker import ScalarFormatter
from cytostream.tools import rgb_to_hex, get_cmap_blues, get_file_sample_stats, get_all_colors
from cytostream.tools import set_logicle_transformed_ticks, set_scatter_ticks, set_log_transformed_ticks
from cytostream.tools import get_fontsize, get_fontname, set_logicle_transformed_ticks
from cytostream.tools import set_scatter_ticks,set_log_transformed_ticks
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
        ax.scatter([dataX],[dataY],c='gray',s=ms,edgecolor='none',alpha=0.2)
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

            ## plot events            
            nonBorderEvents = np.array(list(set(range(len(indicesFG))).difference(set(borderEvents))))
            if nonBorderEvents.size > 0:       
                colorList = bilinear_interpolate(dataX[nonBorderEvents],dataY[nonBorderEvents],bins=colorList)
                ax.scatter([dataX[nonBorderEvents]],[dataY[nonBorderEvents]],c=colorList,s=1,edgecolor='none',cmap=myCmap)
            if borderEvents.size > 0:
                ax.scatter([dataX[borderEvents]],[dataY[borderEvents]],c='k',s=1,edgecolor='none')
        elif drawState == 'scatter':
            dataX,dataY = (events[indicesFG,index1],events[indicesFG,index2])
            ax.scatter([dataX],[dataY],c=colorList,s=markerSize,edgecolor='none')

def draw_labels(ax,events,indicesFG,indicesBG,index1,index2,labels,markerSize,highlight,centroids,numSubplots,drawState):
    """
    draw the labels based on sample centroids in a plot based on foreground and background

    """

    colorList = get_all_colors()

    if str(labels) == "None":
        return

    if centroids == None:
        print "WARNING: BasePlotters: cannot specify highlight without centroids"
        return
    
    if not len(indicesFG) > 0:
        return

    def draw_centroid(l,index1,index2,labelSize):
        
        labelColor = "#C0C0C0"
        alphaVal = 0.9

        if centroids.has_key(str(int(l))) == False:
            return

        if drawState == 'scatter':
            labelColor = colorList[l]

        xPos = centroids[str(int(l))][index1]
        yPos = centroids[str(int(l))][index2]

        fontColor = 'black'
        if labelColor in ['k','b',"#002200","#660033","#990033"]:
            fontColor = 'white'

        ax.text(xPos, yPos, '%s%s'%(prefix,l),color=fontColor,fontsize=labelSize,
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

    ## adjust label size based on number of clusters
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

def finalize_draw(ax,events,channelDict,index1,index2,transform,fontSize,fontName,useSimple=False,axesOff=False,useScaled=False):

    ## variables
    scatterList = ['FSC','FSCA','FSCW','FSCH','SSC','SSCA','SSCW','SSCH']
    xTransformed, yTransformed = False, False
    buff = 0.02
    formatter = ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-3,3))

    ## handle data edge buffers
    def scaled_axis(axis):
        if axis == 'x':
            bufferX = buff * (events[:,index1].max() - events[:,index1].min())
            ax.set_xlim([events[:,index1].min()-bufferX,events[:,index1].max()+bufferX])
        elif axis == 'y':
            bufferY = buff * (events[:,index2].max() - events[:,index2].min())
            ax.set_ylim([events[:,index2].min()-bufferY,events[:,index2].max()+bufferY])

    ## check to see if we force scale the axes
    if channelDict.has_key('time') and index1 == channelDict['time']:
        scaled_axis('x')
        xTransformed = True
        ax.xaxis.set_major_formatter(formatter)
    if channelDict.has_key('time') and index2 == channelDict['time']:
        scaled_axis('y')
        ax.yaxis.set_major_formatter(formatter)
        yTransformed = True

    ## handle scatter axes
    for key,val in channelDict.iteritems():
        if xTransformed == False and key in scatterList and index1 == val:
            set_scatter_ticks(ax,'x',fontsize=fontSize,fontname=fontName)
            xTransformed = True
        if yTransformed == False and key in scatterList and index2 == val:
            set_scatter_ticks(ax,'y',fontsize=fontSize,fontname=fontName)
            yTransformed = True

    ## handle other channels
    if xTransformed == False and transform == 'logicle':
        set_logicle_transformed_ticks(ax,axis='x',fontsize=fontSize,fontname=fontName)
    elif xTransformed == False and transform == 'log':
        set_log_transformed_ticks(ax,axis='x',fontsize=fontSize,fontname=fontName)

    if yTransformed == False and transform == 'logicle':
        set_logicle_transformed_ticks(ax,axis='y',fontsize=fontSize,fontname=fontName)
    elif yTransformed == False and transform == 'log':
        set_logicle_transformed_ticks(ax,axis='y',fontsize=fontSize,fontname=fontName)

    ## check to see if we force scale the axes
    if useScaled == True:
        scaled_axis('x')
        scaled_axis('y')
        
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

    ## ensure the same fontsize, type
    for t in ax.get_yticklabels():
        t.set_fontsize(fontSize)
        t.set_fontname(fontName)

    for t in ax.get_xticklabels():
        t.set_fontsize(fontSize)
        t.set_fontname(fontName)
      
    ## make axes square
    ax.set_aspect(1./ax.get_data_ratio())

def draw_plot(args,parent=None,axesOff=False,markerSize=1):
    ''' 
    draw_plot takes args to create a plot 
    can be entirely independent of classes however a parent
    or a CytostreamPlotter instance may be provided 

    args[0] = ax                       [required]  matplotlib axes
    args[1] = events                   [required]  np.array (N,D)
    args[2] = channelList              [required]  channel listx
    args[3] = channelDict              [required]  cytostream channel dict
    args[4] = channel1Index            [required]  int
    args[5] = channel2Index            [required]  int
    args[6] = subsample                [required]  float | 'original'
    args[7] = transform                [required]  'log' | 'logicle'
    args[8] = labels                   [optional]  np.array (N,1)
    args[9] = subplotHighlight         [optional]  None|clusterID (str(int))
    args[10] = logger                   [optional]  Logger instance
    args[11] = drawState               [optional]  scatter | heat | contour
    args[12] = numSubplots             [optional]  int 1-16
    args[13] = axisLabels              [optional]  True | False
    args[14] = plotTitle               [optional]  None | str
    args[15] = showNoise               [optional]  True | False
    args[16] = useSimple               [optional]  False | True
    args[17] = useScaled               [optional]  False | True
    args[18] = isGui                   [optional]  False | True

    '''

    ## handle args
    ax           = args[0]
    events       = args[1]
    channelList  = args[2]
    channelDict  = args[3]
    channel1Ind  = args[4]
    channel2Ind  = args[5]
    subsample    = args[6]
    transform    = args[7]
    labels       = args[8]
    highlight    = args[9]
    log          = args[10]
    drawState    = args[11]
    numSubplots  = args[12]
    axesLabels   = args[13]
    plotTitle    = args[14]
    showNoise    = args[15]
    useSimple    = args[16]
    useScaled    = args[17]
    isGui        = args[18]

    ## force drawState to heat if necessary
    if labels == None and drawState != 'heat':
        msg = "Forcing draw state to heat because labels were not provided"
        if parent != None:
            reply = QtGui.QMessageBox.warning(parent, "Warning", msg)
            parent.vizSelector.btns['heat'].setChecked(True)
            parent.vizSelector.selectedItem = 'heat'
            parent.drawState = 'heat'
        else:
            print "WARNING:"+msg
        drawState = 'heat'

    ## handle subsampling by ensuring subsample Inds are present
    n,d = events.shape
    if type(np.array([])) == type(subsample):
        randEvents = subsample
    elif type(0) == type(subsample):
        if subsample < n:
            ssSize = subsample
        else:
            ssSize = n

        randEvents = np.arange(ssSize)
        np.random.shuffle(randEvents)
        print 'BasePlotters DBG -- creating random events'
    elif subsample == 'original':
        pass
    else:
        print "WARNING: BasePlotters.py draw_plot -- subsample must be the array or an int or 'original' not ", type(subsample)
        
    ## ensure that subsample size is appropriate
    if subsample == 'original':
        subsampleInds = np.arange(events.shape[0])
    elif randEvents.size > n:
        subsampleInds = randEvents[:n]
    else:
        subsampleInds = randEvents

    ## other variables
    centroids = None
    masterColorList = get_all_colors()
    fontName = get_fontname()
    fontSize = get_fontsize(numSubplots)

    if numSubplots == None:
        numSubplots = 1

    ## clear axis
    ax.clear()
    
    if type(labels) == type([]):
        labels = np.array(labels)

    ## specify channels
    if parent != None:
        channel1Ind = int(parent.selectedChannel1)
        channel2Ind = int(parent.selectedChannel2)
    
    # determine of the events those to plot
    eventsToPlot = events[subsampleInds,:]

    if str(labels) != "None" and eventsToPlot.shape[0] != len(labels):
        print "ERROR: draw_plot labels and events do not match", eventsToPlot.shape[0], len(labels)

    ## get centroids
    if parent != None and str(labels) != "None":
        centroids,variances,sizes = parent.currentCentroids
    if parent == None and str(labels) != "None":
        centroids,variances,sizes = get_file_sample_stats(eventsToPlot,labels)

    ## error check
    if str(labels) != "None":
        if eventsToPlot.shape[0] != labels.size:
            print "ERROR: draw_plot -- labels and events do not match",n,labels.size
            return None

    ## handle highlighting
    totalPts,totalDims = eventsToPlot.shape

    if str(highlight) != "None" and str(labels) == "None":
        print "ERROR in BasePlotters highlight cannot be specified without labels"

    if str(highlight) != "None" and type(highlight) != type([]):
        print "ERROR: in BasePlotters highlight call must be of type list"
    
    if str(highlight) != "None" and type(highlight) == type([]) and str(labels) != "None":

        indicesFG = np.array([])
        if type(highlight) != type([]):
            highlight = [highlight]
        elif type(highlight) == type([]) and len(highlight) == 0:
            highlight = []
        elif type(highlight[0]) == type([]):
            highlight = highlight[0]

        for clustID in highlight:
            if int(clustID) not in labels:
                continue                
            indicesFG = np.hstack([indicesFG, np.where(labels==int(clustID))[0]])
        
        _indices = np.array([int(i) for i in indicesFG])
        if len(_indices) > 0:
            indicesFG = subsampleInds[_indices]
            colorList = masterColorList[labels[_indices]]
        else:
            colorList = None
            indicesFG = []

        indicesBG = list(set(subsampleInds).difference(set(indicesFG)))
    else:
        indicesFG = subsampleInds
        indicesBG = []
        colorList = masterColorList[labels]

    ## draw the points
    if str(labels) != "None" and drawState == 'scatter':
        if max(labels) > len(masterColorList):
            print "WARNING: BasePlotters.draw_plot not enough colors in master color list"
    elif drawState == 'heat':
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
            draw_labels(ax,events,indicesFG,indicesBG,channel1Ind,channel2Ind,labels,markerSize,highlight,centroids,numSubplots,drawState)
        
        ## handle title and labels
        ####if parent != None and parent.title_cb.isChecked() == True and plotTitle != None:
        ####    plotTitle = re.sub("_"," ",plotTitle)
        ####    parent.ax.set_title(plotTitle,fontname=fontName,fontsize=fontSize)

        ####if parent != None and parent.axLab_cb.isChecked == False:
        ####    pass
        if axesLabels == False:
            pass
        else:
            if len(channelList) < channel1Ind + 1:
                print "WARNING: draw_plot -- bad channel index specified max(%s)"%len(channelList), channel1Ind 
            else:
                ax.set_xlabel(re.sub("_"," ",channelList[channel1Ind]),fontname=fontName,fontsize=fontSize)
            if len(channelList) < channel2Ind + 1:
                print "WARNING: draw_plot -- bad channel index specified max(%s)"%len(channelList), channel2Ind 
            else:
                ax.set_ylabel(re.sub("_"," ",channelList[channel2Ind]),fontname=fontName,fontsize=fontSize)
                if isGui == True:
                    ax.yaxis.set_label_position('right')

        if plotTitle != None and plotTitle != False:
            plotTitle = re.sub("_"," ",plotTitle)
            ax.set_title(plotTitle,fontname=fontName,fontsize=fontSize)

        finalize_draw(ax,eventsToPlot,channelDict,channel1Ind,channel2Ind,transform,fontSize,fontName,useSimple,axesOff,useScaled=useScaled)
    else:
        print "ERROR: BasePlotters: draw state not implemented", drawState

    return indicesFG


def create_cytokine_subplot(nga,ax,fileName,index1,index2,filterID,fThreshold,bins=120,fontSize=7,fontName='sans',
                            yLabel='default',xLabel='default',title=None,yLim=None,xLim=None,
                            useColor=True,transform=('logicle','x')):
    if useColor == True:
        myCmap = mpl.cm.gist_heat
        scatterColor = 'blue'
        thresholdColor = 'orange'
    else:
        myCmap = mpl.cm.gray
        scatterColor = '#555555'
        thresholdColor = 'k'

    ## load events
    events = nga.get_events(fileName)
    if filterID != None:
        filterInds = nga.get_filter_indices(fileName,filterID)
        if filterInds.size > 1:
            events = events[filterInds,:]

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
        ax.set_xlabel(fileChannels[index1],fontname=fontName,fontsize=fontSize)
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
