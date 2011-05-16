import sys,os,re
import numpy as np

'''
the functions here use CytostreamPlotter.py as a parent

'''

def draw_scatter(parent,events=None,dataSetName=None,channel1Ind=None,
                 channel2Ind=None,subsample=None,labels=None, modelName='run1',highlight=None,log=None):

    buff = 0.02
    centroids = None
    if channel1Ind != None:
        parent.selectedChannel1=channel1Ind
        parent.channel1Selector.setCurrentIndex(parent.selectedChannel1)
    if channel2Ind != None:
        parent.selectedChannel2=channel2Ind
        parent.channel2Selector.setCurrentIndex(parent.selectedChannel2)

    if events != None:
        parent.events=events
        parent.dataSetName=dataSetName
        parent.subsample=subsample
        parent.labels=labels
        parent.modelName = modelName
        parent.highlight=highlight
        parent.log=log

    if parent.highlight == "None":
        parent.highlight = None

    ## clear axis
    parent.ax.clear()
    parent.ax.grid(parent.grid_cb.isChecked())

    ## declare variables
    if parent.log == None:
        fontName = 'Arial'
        markerSize = 1
        fontSize = 10
        plotType = 'png'
        filterInFocus = None
    else:
        fontName = parent.log.log['font_name']
        markerSize = int(parent.log.log['scatter_marker_size'])
        fontSize = int(parent.log.log['font_size'])
        plotType = parent.log.log['plot_type']
        filterInFocus = parent.log.log['filter_in_focus']

    ## specify channels
    index1 = int(parent.selectedChannel1)
    index2 = int(parent.selectedChannel2)
    channel1 = parent.fileChannels[index1]
    channel2 = parent.fileChannels[index2]

    ## get centroids
    if parent.labels != None:
        plotID, channelsID = parent.pdo.get_ids(parent.dataSetName,parent.subsample,parent.modelName,index1,index2)
        centroids = parent.pdo.get_centroids(parent.events,parent.labels,plotID,channelsID)

    ## error check
    if parent.labels != None:
        n,d = parent.events.shape
        if n != parent.labels.size:
            print "ERROR: ScatterPlotter.py -- labels and events do not match",n,labels.size
            return None

    ## make plot
    totalPoints = 0
    if parent.labels == None:
        dataX,dataY = (parent.events[:,index1],parent.events[:,index2])
        parent.ax.scatter([dataX],[dataY],color='blue',s=markerSize)
    else:
        if type(np.array([])) != type(parent.labels):
            parent.labels = np.array(parent.labels)

        numLabels = np.unique(parent.labels).size
        maxLabel = np.max(parent.labels)

        for l in np.sort(np.unique(parent.labels)):
            clusterColor = parent.colors[l]
            markerSize = int(markerSize)

            ## handle highlighted clusters      
            if parent.highlight != None and str(int(parent.highlight)) == str(int(l)):
                alphaVal = 0.8
                markerSize =  markerSize+4
            elif parent.highlight !=None and str(int(parent.highlight)) != str(int(l)):
                alphaVal = 0.5
                clusterColor = "#CCCCCC"
            else:
                alphaVal=0.8

            ## check to see if centorids are already available
            dataX = parent.events[:,index1][np.where(parent.labels==l)[0]]
            dataY = parent.events[:,index2][np.where(parent.labels==l)[0]]
            
            totalPoints+=dataX.size

            if dataX.size == 0:
                continue
            parent.ax.scatter(dataX,dataY,color=clusterColor,s=markerSize)

            ## handle centroids if present     
            prefix = ''

            if centroids != None:
                if centroids[str(int(l))].size != parent.events.shape[1]:
                    print "ERROR: ScatterPlotter.py -- centroids not same shape as events" 
                    
                xPos = centroids[str(int(l))][index1]
                yPos = centroids[str(int(l))][index2]

                if xPos < 0 or yPos <0:
                    continue

                if clusterColor in ['#FFFFAA','y','#33FF77','#CCFFAA',"#CCCCCC"]:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=fontSize,
                                 ha="center", va="center",
                                 bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                 )
                else:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=fontSize,
                                 ha="center", va="center",
                                 bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                 )

    ## handle data edge buffers
    bufferX = buff * (parent.events[:,index1].max() - parent.events[:,index1].min())
    bufferY = buff * (parent.events[:,index2].max() - parent.events[:,index2].min())
    parent.ax.set_xlim([parent.events[:,index1].min()-bufferX,parent.events[:,index1].max()+bufferX])
    parent.ax.set_ylim([parent.events[:,index2].min()-bufferY,parent.events[:,index2].max()+bufferY])

    ## force square axes
    parent.ax.set_aspect(1./parent.ax.get_data_ratio())

    ## save file
    parent.ax.set_title("%s_%s_%s"%(channel1,channel2,parent.dataSetName),fontname=fontName,fontsize=fontSize)
    parent.ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
    parent.ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)
    
    for t in parent.ax.get_xticklabels():
        t.set_fontsize(fontSize)
        t.set_fontname(fontName)
    
    for t in parent.ax.get_yticklabels():
        t.set_fontsize(fontSize)
        t.set_fontname(fontName)
    
    if parent.forceScale == True:
        ax.set_xlim(parent.xAxLimit)
        ax.set_ylim(parent.yAxLimit)

    parent.canvas.draw()
