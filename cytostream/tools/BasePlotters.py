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

def finalize_draw(ax,events,channelDict,index1,index2,transform,fontSize,fontName,useSimple=False,axesOff=False):
    
    ## handle scatter axes
    scatterList = ['fsc','fsc-a','fsc-w','fsc-h','ssc','ssc-a','ssc-w','ssc-h']    
    xTransformed, yTransformed = False, False
    for key,val in channelDict.iteritems():
        if key in scatterList and index1 == val:
            set_scatter_ticks(ax,'x',fontsize=fontSize,fontname=fontName)
            xTransformed = True
        if key in scatterList and index2 == val:
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

    ## make axes square
    ax.set_aspect(1./ax.get_data_ratio())

def draw_plot(args,parent=None,axesOff=False):
    ''' 
    draw_plot takes args to create a plot 
    can be entirely independent of classes however a parent
    or a CytostreamPlotter instance may be provided 

    args[0] = ax                       [required]  matplotlib axes
    args[1] = events                   [required]  np.array (N,D)
    args[2] = channelDict              [required]  cytostream channel dict
    args[3] = channel1Index            [required]  int
    args[4] = channel2Index            [required]  int
    args[5] = subsample                [required]  float | 'original'
    args[6] = transform                [required]  'log' | 'logicle'
    args[7] = labels                   [optional]  np.array (N,1)
    args[8] = subplotHighlight         [optional]  None|clusterID (str(int))
    args[9] = logger                   [optional]  Logger instance
    args[10] = drawState               [optional]  scatter | heat | contour
    args[11] = numSubplots             [optional]  int 1-16
    args[12] = axesLabels              [optional]  None | (xAxisLabel,yAxisLabel)
    args[13] = plotTitle               [optional]  None | str
    args[14] = showNoise               [optional]  True | False
    args[15] = useSimple               [optional]  False | True

    '''

    ## handle args
    ax           = args[0]
    events       = args[1]
    channelDict  = args[2]
    channel1Ind  = args[3]
    channel2Ind  = args[4]
    subsample    = args[5]
    transform    = args[6]
    labels       = args[7]
    highlight    = args[8]
    log          = args[9]
    drawState    = args[10]
    numSubplots  = args[11]
    axesLabels   = args[12]
    plotTitle    = args[13]
    showNoise    = args[14]
    useSimple    = args[15]

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
        n,d = events.shape
        if n != labels.size:
            print "ERROR: ScatterPlotter.py -- labels and events do not match",n,labels.size
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
        if parent != None and parent.title_cb.isChecked() == True and plotTitle != None:
            parent.ax.set_title(plotTitle,fontname=fontName,fontsize=fontSize)
        
        #if parent != None and parent.axLab_cb.isChecked() == True:
        #    ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
        #    ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

        if axesLabels != None:
            if parent != None and parent.axLab_cb.isChecked == False:
                pass
            else:
                if axesLabels[0] != None:
                    ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
                if axesLabels[1] != None:
                    ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)

        if plotTitle != None:
            ax.set_title(subplotTitle,fontname=fontName,fontsize=fontSize)

        finalize_draw(ax,events,channelDict,channel1Ind,channel2Ind,transform,fontSize,fontName,useSimple,axesOff)
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
