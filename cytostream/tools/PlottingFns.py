#!/usr/bin/python
#
# to run an example
# python RunMakeFigures.py -p Demo -i 0 -j 1 -f 3FITC_4PE_004.fcs -h ./projects/Demo
#

import getopt,sys,os,re,csv
import numpy as np

## important line to fix popup error in mac osx
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import MaxNLocator


def get_n_color_colorbar(n,cmapName='jet'):# Spectral #gist_rainbow                                                                                                     
    "breaks any matplotlib cmap into n colors"
    cmap = cm.get_cmap(cmapName,n)
    return cmap(np.arange(n))

def rgb_to_hex(rgb):
    """                                                                                                                                                                      
    converts a rgb 3-tuple into hex                                                                                                                                          
    """

    return '#%02x%02x%02x' % rgb[:3]

def pyfcm_load_fcs_file(filePath):
    data = fcm.loadFCS(filePath)
    return data

def get_file_channel_list(filePath):
    data = pyfcm_load_fcs_file(filePath)
    channels = data.channels
    channels = [re.sub("\s","-",c) for c in channels]
    return channels

def make_scatter_plot(filePath,channel1Ind,channel2Ind,fileChannels,subset='all',labels=None,buff=0.02,altDir=None,centroids=None):
    markerSize = 3
    alphaVal = 0.5

    fontName = 'arial'
    fontSize = 12
    plotType = 'png'

    colors = ['b','g','r','c','m','y','k','orange','#AAAAAA','#FF6600',
              '#FFCC00','#FFFFAA','#6622AA','#33FF77','#998800','#0000FF',
              '#FA58AC','#8A0808','#D8D8D8','#336666','#996633',"#FFCCCC",
              "#FF9966","#009999","#FF0099","#996633","#990000","#660000",
              "#330066","#99FF99","#FF99FF","#333333","#CC3333","#CC9900",
              "#003333","#66CCFF","#CCFFFF","#FFCCFF","#009999"]

    #colors = ['b','g','r','c','m','y','b','orange','#AAAAAA','#FF6600','#FFCC00',
    #          '#FFFFAA','#6622AA','#33FF77','#998800']

    ## prepare figure
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111)

    ## specify channels
    index1 = int(channel1Ind)
    index2 = int(channel2Ind)
    
    channel1 = fileChannels[index1]
    channel2 = fileChannels[index2]

    ## exclude scatter
    #data = pyfcm_load_fcs_file(filePath)
    data = read_txt_into_array(filePath)

    ## make plot
    totalPoints = 0
    if labels == None:
        ax.scatter([data[:,index1]],[data[:,index2]],color='blue',s=markerSize)
    else:
        if type(np.array([])) != type(labels):
            labels = np.array(labels)

        numLabels = np.unique(labels).size
        maxLabel = np.max(labels)

        clustCount = -1
        for l in np.sort(np.unique(labels)):
            hexColor = colors[l]
            clustCount += 1

            x = data[:,index1][np.where(labels==l)[0]]
            y = data[:,index2][np.where(labels==l)[0]]
            
            totalPoints+=x.size

            if x.size == 0:
                continue
            ax.scatter(x,y,color=hexColor,s=markerSize)

            ## handle centroids if present
            prefix = ''
            if centroids != None:
                xPos = centroids[str(l)][index1]
                yPos = centroids[str(l)][index2]

                if colors[l] in ['#FFFFAA','y']:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=hexColor)
                            )
                else:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white',
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=hexColor)
                            )

    ## handle data edge buffers
    bufferX = buff * (data[:,index1].max() - data[:,index1].min())
    bufferY = buff * (data[:,index2].max() - data[:,index2].min())
    ax.set_xlim([data[:,index1].min()-bufferX,data[:,index1].max()+bufferX])
    ax.set_ylim([data[:,index2].min()-bufferY,data[:,index2].max()+bufferY])

    ## save file
    fileName = os.path.split(filePath)[-1]
    ax.set_title("%s_%s_%s"%(channel1,channel2,fileName),fontname=fontName,fontsize=fontSize)
    ax.set_xlabel(channel1,fontname=fontName,fontsize=fontSize)
    ax.set_ylabel(channel2,fontname=fontName,fontsize=fontSize)
    
    if altDir == None:
        print "ERROR: must specify altDir, not saving figure"
    else:
        fileName = os.path.join(altDir,"%s_%s_%s.%s"%(re.sub("\.fcs|\.out","",fileName),channel1,channel2,plotType))
        fig.savefig(fileName,transparent=False,dpi=200)


def make_plots_as_subplots(expListNames,expListData,expListLabels,colInd1=0,colInd2=1,centroids=None,colInd1Name=None, colInd2Name=None,
                           showCentroids=True,figTitle=None,markerSize=5,saveas=None,fileChannels=None,subplotRows=3,subplotCols=2,refFile=None):
    if subplotRows > subplotCols:
        fig = plt.figure(figsize=(6.5,9))
    elif subplotCols > subplotRows:
        fig = plt.figure(figsize=(9,6.5))
    else:
        fig = plt.figure(figsize=(9,8))

    
    #for key,item in centroids.iteritems():
    #    print "\t", key,item.keys()


    subplotCount = 0
    colors = ['b','g','r','c','m','y','k','orange','#AAAAAA','#FF6600',
              '#FFCC00','#FFFFAA','#6622AA','#33FF77','#998800','#0000FF',
              '#FA58AC','#8A0808','#D8D8D8','#336666','#996633',"#FFCCCC",
              "#FF9966","#009999","#FF0099","#996633","#990000","#660000",
              "#330066","#99FF99","#FF99FF","#333333","#CC3333","#CC9900",
              "#003333","#66CCFF","#CCFFFF","#FFCCFF","#009999"]

    ## determin the ymax and xmax
    xMaxList, yMaxList, xMinList, yMinList = [],[],[],[]
    for c in range(len(expListNames)):
        expData = expListData[c]
        labels = expListLabels[c]
        expName = expListNames[c]
        #if expName == "ACS-T-Pt_5_SEB":
        #    continue

        xMaxList.append(expData[:,colInd1].max())
        yMaxList.append(expData[:,colInd2].max())
        xMinList.append(expData[:,colInd1].min())
        yMinList.append(expData[:,colInd2].min())

    xAxLimit = (0 - 0.05, np.array(xMaxList).max() + 0.05 * np.array(xMaxList).max())
    yAxLimit = (0 - 0.05, np.array(yMaxList).max() + 0.05 * np.array(yMaxList).max())


    #xAxLimit = (np.array(xMinList).min() - 0.05 * np.array(xMinList).min(), np.array(xMaxList).max() + 0.05 * np.array(xMaxList).max())
    #yAxLimit = (np.array(yMinList).min() - 0.05 * np.array(yMinList).min(), np.array(yMaxList).max() + 0.05 * np.array(yMaxList).max())

    for c in range(len(expListNames)):
        expData = expListData[c]
        labels = expListLabels[c]
        expName = expListNames[c]
        subplotCount += 1
        ax = fig.add_subplot(subplotRows,subplotCols,subplotCount)
        ax.clear()

        totalPoints = 0
        for l in np.sort(np.unique(labels)):
            try:
                clustColor = colors[l]
            except:
                print 'WARNING not enough colors in self.colors looking for ', l
                clustColor = 'black'

            x = expData[:,colInd1][np.where(labels==l)[0]]
            y = expData[:,colInd2][np.where(labels==l)[0]]

            if x.size == 0:
                continue

            ax.scatter(x,y,color=clustColor,s=markerSize)
            totalPoints+=x.size

            ## handle centroids if present
            prefix = ''
            if centroids != None and showCentroids == True:
                xPos = centroids[expName][str(l)][colInd1]
                yPos = centroids[expName][str(l)][colInd2]
                
                if clustColor in ['#FFFFAA','y','#33FF77']:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=8.0,
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=clustColor,alpha=0.8)
                            )
                else:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=8.0,
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=clustColor,alpha=0.8)
                            )

        ## error check that all point were plotted 
        if totalPoints != expData[:,0].size:
            print "ERROR: the correct number of point were not plotted %s/%s"%(totalPoints,expData[:,0].size)

        if expListNames[subplotCount-1] == refFile:
            ax.set_title(expListNames[subplotCount-1],fontweight='heavy')
        else:
            ax.set_title(expListNames[subplotCount-1])

        ax.set_xlim([xAxLimit[0],xAxLimit[1]])
        ax.set_ylim([yAxLimit[0],yAxLimit[1]])

        ax.xaxis.set_major_locator(MaxNLocator(4))
        ax.yaxis.set_major_locator(MaxNLocator(4))

        leftSidePanels = np.arange(1,subplotCols*subplotRows+1,subplotCols)
        bottomPanels = np.arange(1,subplotCols*subplotRows+1)[-subplotCols:]

        if subplotCount not in leftSidePanels:
            ax.set_yticks([])
        else:
            if colInd2Name != None:
                ax.set_ylabel(colInd2Name)

        if subplotCount not in bottomPanels:
            ax.set_xticks([])
        else:
            if colInd1Name != None:
                ax.set_xlabel(colInd1Name)

        if figTitle != None:
            fig.suptitle(figTitle, fontsize=12)

        plt.subplots_adjust(wspace=0.1, hspace=0.2)

        if saveas != None:
            fig.savefig(saveas,dpi=300)
