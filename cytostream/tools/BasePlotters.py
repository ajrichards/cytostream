import sys,os,re
import numpy as np

import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from matplotlib.nxutils import points_inside_poly
from cytostream.tools import rgb_to_hex, get_cmap_blues
from fcm.graphics import bilinear_interpolate
'''
the functions here use CytostreamPlotter.py as a parent

'''

def draw_scatter(parent,events=None,selectedFileName=None,channel1Ind=None,
                 channel2Ind=None,subsample=None,labels=None, modelRunID='run1',highlight=None,log=None):

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
        parent.selectedFileName=selectedFileName
        parent.subsample=subsample
        parent.labels=labels
        parent.modelRunID = modelRunID
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
        fontSize = 10
        plotType = 'png'
        filterInFocus = None
    else:
        fontName = parent.log.log['font_name']
        fontSize = int(parent.log.log['font_size'])
        plotType = parent.log.log['plot_type']
        filterInFocus = parent.log.log['filter_in_focus']

    markerSize = parent.markerSize

    ## specify channels
    index1 = int(parent.selectedChannel1)
    index2 = int(parent.selectedChannel2)
    channel1 = parent.fileChannels[index1]
    channel2 = parent.fileChannels[index2]

    ## get centroids
    if str(parent.labels) != "None":
        plotID, channelsID = parent.pdo.get_ids(parent.selectedFileName,parent.subsample,parent.modelRunID,index1,index2)
        centroids = parent.pdo.get_centroids(parent.events,parent.labels,plotID,channelsID)

    ## error check
    if str(parent.labels) != "None":
        n,d = parent.events.shape
        if n != parent.labels.size:
            print "ERROR: ScatterPlotter.py -- labels and events do not match",n,labels.size
            return None

    ## make plot
    if str(parent.labels) == "None":
        dataX,dataY = (parent.events[:,index1],parent.events[:,index2])
        parent.ax.scatter([dataX],[dataY],color='blue',s=markerSize)
    else:
        if type(np.array([])) != type(parent.labels):
            parent.labels = np.array(parent.labels)

        numLabels = np.unique(parent.labels).size
        maxLabel = np.max(parent.labels)
        highlightSaved = None
        for l in np.sort(np.unique(parent.labels)):
            clusterColor = parent.colors[l]
            markerSize = parent.markerSize
            clusterInds = np.where(parent.labels==l)[0]

            ## handle highlighted clusters      
            if parent.highlight != None and str(int(parent.highlight)) == str(int(l)):
                alphaVal = 0.8
                markerSize =  markerSize+4
                highlightSaved = {'ms':markerSize, 'alpha':alphaVal,'num':l}
                dataX = parent.events[:,index1][clusterInds]
                dataY = parent.events[:,index2][clusterInds]
                highlightSaved['x'] = dataX
                highlightSaved['y'] = dataY
                highlightSaved['color'] = clusterColor
                continue 
            elif parent.highlight !=None and str(int(parent.highlight)) != str(int(l)):
                alphaVal = 0.5
                clusterColor = "#CCCCCC"
            else:
                alphaVal=0.8

            ## check to see if centorids are already available
            dataX = parent.events[:,index1][clusterInds]
            dataY = parent.events[:,index2][clusterInds]

            if dataX.size == 0:
                continue
            parent.ax.scatter(dataX,dataY,color=clusterColor,s=markerSize)

            ## handle centroids if present     
            prefix = ''

            if centroids != None and parent.labels_cb.isChecked():
                if centroids[str(int(l))].size != parent.events.shape[1]:
                    print "ERROR: ScatterPlotter.py -- centroids not same shape as events" 
                    
                xPos = centroids[str(int(l))][index1]
                yPos = centroids[str(int(l))][index2]

                if xPos < 0 or yPos <0:
                    continue

                if clusterColor in ['#FFFFAA','y','#33FF77','#CCFFAA',"#CCCCCC"]:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=fontSize-1,
                                 ha="center", va="center",
                                 bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                 )
                else:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=fontSize-1,
                                 ha="center", va="center",
                                 bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                 )

        if highlightSaved != None:

            parent.ax.scatter(highlightSaved['x'],highlightSaved['y'],color=highlightSaved['color'],s=highlightSaved['ms'])
            xPos = centroids[str(int(highlightSaved['num']))][index1]
            yPos = centroids[str(int(highlightSaved['num']))][index2]
            
            if parent.labels_cb.isChecked():
                if highlightSaved['color'] in ['#FFFFAA','y','#33FF77','#CCFFAA',"#CCCCCC"]:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,highlightSaved['num']), color='black',fontsize=fontSize-1,
                                   ha="center", va="center",
                                   bbox = dict(boxstyle="round",facecolor=highlightSaved['color'],alpha=highlightSaved['alpha'])
                                   )
                else:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,highlightSaved['num']), color='white', fontsize=fontSize-1,
                                   ha="center", va="center",
                                   bbox = dict(boxstyle="round",facecolor=highlightSaved['color'],alpha=highlightSaved['alpha'])
                                   )

    ## handle data edge buffers
    bufferX = buff * (parent.events[:,index1].max() - parent.events[:,index1].min())
    bufferY = buff * (parent.events[:,index2].max() - parent.events[:,index2].min())
    parent.ax.set_xlim([parent.events[:,index1].min()-bufferX,parent.events[:,index1].max()+bufferX])
    parent.ax.set_ylim([parent.events[:,index2].min()-bufferY,parent.events[:,index2].max()+bufferY])

    ## force square axes
    parent.ax.set_aspect(1./parent.ax.get_data_ratio())

    ## save file
    if parent.title_cb.isChecked() == True:
        parent.ax.set_title("%s_%s_%s"%(channel1,channel2,parent.selectedFileName),fontname=fontName,fontsize=fontSize)
    
    if parent.axLab_cb.isChecked() == True:
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


def draw_heat_scatter(parent,events=None,selectedFileName=None,channel1Ind=None,
                      channel2Ind=None,subsample=None,labels=None, modelRunID='run1',highlight=None,log=None):

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
        parent.selectedFileName=selectedFileName
        parent.subsample=subsample
        parent.labels=labels
        parent.modelRunID = modelRunID
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
        fontSize = 10
        plotType = 'png'
        filterInFocus = None
    else:
        fontName = parent.log.log['font_name']
        fontSize = int(parent.log.log['font_size'])
        plotType = parent.log.log['plot_type']
        filterInFocus = parent.log.log['filter_in_focus']

    markerSize = parent.markerSize

    ## specify channels
    index1 = int(parent.selectedChannel1)
    index2 = int(parent.selectedChannel2)
    channel1 = parent.fileChannels[index1]
    channel2 = parent.fileChannels[index2]

    ## get centroids
    if str(parent.labels) != "None":
        plotID, channelsID = parent.pdo.get_ids(parent.selectedFileName,parent.subsample,parent.modelRunID,index1,index2)
        centroids = parent.pdo.get_centroids(parent.events,parent.labels,plotID,channelsID)

    ## error check
    if str(parent.labels) != "None":
        n,d = parent.events.shape
        if n != parent.labels.size:
            print "ERROR: ScatterPlotter.py -- labels and events do not match",n,labels.size
            return None

    ## make plot
    
    if type(np.array([])) != type(parent.labels):
        parent.labels = np.array(parent.labels)
        
    numLabels = np.unique(parent.labels).size
    maxLabel = np.max(parent.labels)
    
    x,y = (parent.events[:,index1],parent.events[:,index2])

    ## axes buffering
    bufferX = buff * (x.max() - x.min())
    bufferY = buff * (y.max() - y.min())
    xMin, xMax = x.min()-bufferX,x.max()+bufferX
    yMin, yMax = y.min()-bufferY,y.max()+bufferY

    myCmap = mpl.cm.gist_heat # spectral hot, gist_heat jet
    totalPts = len(x)
    if totalPts >= 9e04:
        bins = 120.0
    elif totalPts >= 5e04:
        bins = 50.0
    else:
        bins = 40.0
    
    colorList = bilinear_interpolate(x,y,bins=bins)

    if str(parent.labels) == "None":
        parent.ax.scatter(x,y,c=colorList,s=1,edgecolors='none',cmap=myCmap)
    else:
        highlightSaved = None
        for l in np.sort(np.unique(parent.labels)):
            clusterColor = '#FFFFAA'
            markerSize = parent.markerSize
            isBackground = False
            clusterInds = np.where(parent.labels==l)[0]
            dataX = parent.events[:,index1][clusterInds]
            dataY = parent.events[:,index2][clusterInds]

            ## handle highlighted clusters      
            if parent.highlight != None and str(int(parent.highlight)) == str(int(l)):
                alphaVal = 0.8
                markerSize =  markerSize+4
                highlightSaved = {'ms':markerSize, 'alpha':alphaVal,'num':l}
                highlightSaved['x'] = dataX
                highlightSaved['y'] = dataY
                colorSubset = np.array(colorList)[clusterInds]
                colorSubset = colorSubset.tolist()
                highlightSaved['color'] = clusterColor
                continue
            elif parent.highlight !=None and str(int(parent.highlight)) != str(int(l)):
                alphaVal = 0.5
                clusterColor = "#CCCCCC"
                isBackground = True
            else:
                alphaVal=0.8

            ## check to see if centorids are already available 
            if dataX.size == 0:
                continue

            clrs = colorList[clusterInds]

            if isBackground == False:
                parent.ax.scatter(dataX,dataY,c=clrs,s=markerSize,edgecolor='none',cmap=myCmap)
            else:
                parent.ax.scatter(dataX,dataY,color=clusterColor,s=markerSize,edgecolor='none',cmap=myCmap)

            ## handle centroids if present
            prefix = ''

            if centroids != None and parent.labels_cb.isChecked():
                if centroids[str(int(l))].size != parent.events.shape[1]:
                    print "ERROR: ScatterPlotter.py -- centroids not same shape as events" 
                    
                xPos = centroids[str(int(l))][index1]
                yPos = centroids[str(int(l))][index2]

                if xPos < 0 or yPos <0:
                    continue

                if clusterColor in ['#FFFFAA','y','#33FF77','#CCFFAA',"#CCCCCC"]:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=fontSize-1,
                                   ha="center", va="center",
                                   bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                   )
                else:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=fontSize-1,
                                   ha="center", va="center",
                                 bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                   )

        if highlightSaved != None:
            parent.ax.scatter(highlightSaved['x'],highlightSaved['y'],c=colorSubset,s=highlightSaved['ms'],edgecolor='none',cmap=myCmap)
            xPos = centroids[str(int(highlightSaved['num']))][index1]
            yPos = centroids[str(int(highlightSaved['num']))][index2]
            
            if parent.labels_cb.isChecked():
                if highlightSaved['color'] in ['#FFFFAA','y','#33FF77','#CCFFAA',"#CCCCCC"]:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,highlightSaved['num']), color='black',fontsize=fontSize-1,
                                   ha="center", va="center",
                                   bbox = dict(boxstyle="round",facecolor=highlightSaved['color'],alpha=highlightSaved['alpha'])
                                   )
                else:
                    parent.ax.text(xPos, yPos, '%s%s'%(prefix,highlightSaved['num']), color='white', fontsize=fontSize-1,
                                   ha="center", va="center",
                                   bbox = dict(boxstyle="round",facecolor=highlightSaved['color'],alpha=highlightSaved['alpha'])
                                   )
            
    ## handle data edge buffers
    parent.ax.set_xlim(xMin,xMax)
    parent.ax.set_ylim(yMin,yMax)

    ## force square axes
    parent.ax.set_aspect(1./parent.ax.get_data_ratio())

    ## save file
    if parent.title_cb.isChecked():
        parent.ax.set_title("%s_%s_%s"%(channel1,channel2,parent.selectedFileName),fontname=fontName,fontsize=fontSize)
    if parent.axLab_cb.isChecked():
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
