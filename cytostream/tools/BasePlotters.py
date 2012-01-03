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

def finalize_draw(ax,events,channelDict,index1,index2,transform,fontSize,fontName,useSimple=False,axesOff=False,useScaled=False):

    ## variables
    scatterList = ['fsc','fsc-a','fsc-w','fsc-h','ssc','ssc-a','ssc-w','ssc-h']
    xTransformed, yTransformed = False, False
    buff = 0.02

    ## handle data edge buffers
    def scaled_axis(axis):
        #formatter = ScalarFormatter(useMathText=True)
        #formatter.set_scientific(True)
        #formatter.set_powerlimits((-3,3))
        
        if axis == 'x':
            bufferX = buff * (events[:,index1].max() - events[:,index1].min())
            ax.set_xlim([events[:,index1].min()-bufferX,events[:,index1].max()+bufferX])
            #ax.xaxis.set_major_formatter(formatter)
        elif axis == 'y':
            bufferY = buff * (events[:,index2].max() - events[:,index2].min())
            ax.set_ylim([events[:,index2].min()-bufferY,events[:,index2].max()+bufferY])        
            #ax.yaxis.set_major_formatter(formatter)

    ## check to see if we force scale the axes
    #if useScaled == True:
    #    scaled_axis('x')
    #    scaled_axis('y')
    #    xTransformed = True
    #    yTransformed = True
    
    ## check for time scaling
    if channelDict.has_key('time') and index1 == channelDict['time']:
        scaled_axis('x')
        xTransformed = True
    if channelDict.has_key('time') and index2 == channelDict['time']:
        scaled_axis('y')
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

def draw_plot(args,parent=None,axesOff=False):
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

    ## handle subsampling
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
    else:
        print "WARNING: BasePlotters.py draw_plot -- subsample must be the array or an int -- using original data"

    ## ensure that subsample size is appropriate
    if randEvents.size > n:
        subsampleInds = randEvents[:n]
    else:
        subsampleInds = randEvents

    ## other variables
    centroids = None
    markerSize = 1
    masterColorList = get_all_colors()
    fontName = get_fontname()
    fontSize = get_fontsize(numSubplots)

    if parent != None and channel1Ind != None:
        parent.selectedChannel1=channel1Ind
        parent.channel1Selector.setCurrentIndex(parent.selectedChannel1)
    if parent != None and channel2Ind != None:
        parent.selectedChannel2=channel2Ind
        parent.channel2Selector.setCurrentIndex(parent.selectedChannel2)

    if numSubplots == None:
        numSubplots = 1

    ## highlight
    if parent != None and str(parent.selectedHighlight) == "None":
        parent.selectedHighlight = None
    elif parent != None and str(parent.selectedHighlight) != "None":
        highlight = [parent.selectedHighlight]

    ## clear axis
    ax.clear()    
    if parent != None:
        parent.ax.grid(parent.grid_cb.isChecked())
    
    if type(labels) == type([]):
        labels = np.array(labels)

    ## specify channels
    if parent != None:
        channel1Ind = int(parent.selectedChannel1)
        channel2Ind = int(parent.selectedChannel2)
        
    ## get centroids
    #if parent != None and str(labels) != "None":
    #    plotID, channelsID = parent.pdo.get_ids(parent.selectedFileName,parent.subsample,parent.modelRunID,channel1Ind,channel2Ind)
    #    centroids = parent.pdo.get_centroids(parent.events,parent.labels,plotID,channelsID)
    #elif parent == None and str(labels) != "None":
    #    centroids,variances,sizes = get_file_sample_stats(events,labels)

    ## error check
    if str(labels) != "None":
        if n != labels.size:
            print "ERROR: draw_plot -- labels and events do not match",n,labels.size
            return None

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
        indicesBG = list(set(subsampleInds).difference(set(indicesFG)))
    else:
        indicesFG = subsampleInds
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
        if parent != None and parent.title_cb.isChecked() == True and plotTitle != None:
            parent.ax.set_title(plotTitle,fontname=fontName,fontsize=fontSize)
        
        if parent != None and parent.axLab_cb.isChecked == False:
            pass
        elif axesLabels == False:
            pass
        else:
            ax.set_xlabel(channelList[channel1Ind],fontname=fontName,fontsize=fontSize)
            ax.set_ylabel(channelList[channel2Ind],fontname=fontName,fontsize=fontSize)

        if plotTitle != None:
            ax.set_title(plotTitle,fontname=fontName,fontsize=fontSize)

        ## check for forced scaling
        if parent != None and parent.scale_cb.isChecked() == True:
            useScaled = True
        elif parent != None and parent.scale_cb.isChecked() == False:        
            useScaled = False

        finalize_draw(ax,events,channelDict,channel1Ind,channel2Ind,transform,fontSize,fontName,useSimple,axesOff,useScaled=useScaled)
    else:
        print "ERROR: BasePlotters: draw state not implemented", drawState

def create_cytokine_subplot(nga,ax,fileName,index1,index2,filterID,fThreshold,bins=120,fontSize=7,fontName='arial',
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
