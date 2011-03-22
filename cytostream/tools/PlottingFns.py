#!/usr/bin/python
#
# to run an example
# python RunMakeFigures.py -p Demo -i 0 -j 1 -f 3FITC_4PE_004.fcs -h ./projects/Demo
#

import getopt,sys,os,re,csv
import numpy as np
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import MaxNLocator
from cytostream.tools import read_txt_to_file_channels,read_txt_into_array,get_file_data
import fcm

def get_n_color_colorbar(n,cmapName='jet'):# Spectral #gist_rainbow 
    '''
    breaks any matplotlib cmap into n colors
 
    '''
    cmap = cm.get_cmap(cmapName,n)
    return cmap(np.arange(n))

def rgb_to_hex(rgb):
    '''
    converts a rgb 3-tuple into hex
          
    '''

    return '#%02x%02x%02x' % rgb[:3]

def pyfcm_load_fcs_file(filePath):
    data = fcm.loadFCS(filePath)
    return data

def get_file_channel_list(filePath):
    data = pyfcm_load_fcs_file(filePath)
    channels = data.channels
    channels = [re.sub("\s","-",c) for c in channels]
    return channels

def get_all_colors():
    colors =  ['b','#CC6600','g','r','c','m',"#002200",'y','k','orange',"#CC55FF","#990033",'#FF6600',"#CCCCCC","#660033",
               '#FFCC00','#FFFFAA','#6622AA','#33FF77','#998800','#0000FF',"#995599","#00AA00","#777777","#FF0033",'#990066',
               '#FA58AC','#8A0808','#D8D8D8',"#CC2277",'#336666','#996633',"#FFCCCC","#CC0011","#FFBB33","#DDDDDD","#991188"
               "#FF9966","#009999","#FF0099","#996633","#990000","#660000","#9900BB","#330033","#FF5544","#9966CC",
               "#330066","#99FF99","#FF99FF","#333333","#CC3333","#CC9900","#99DD22","#3322BB","#663399","#002255",
               "#003333","#66CCFF","#CCFFFF","#AA11BB","#000011","#FFCCFF","#00EE33","#337722","#CCBBFF","#FF3300",
               "#009999","#110000","#AAAAFF","#990000","#880022","#BBBBBB","#00EE88","#66AA22","#99FFEE","#660022",
               "#FFFF33","#00CCFF","#990066","#006600","#00CCFF",'#AAAAAA',"#33FF00","#0066FF","#FF9900","#FFCC00"]
    return colors

'''
def make_scatter_plot(filePath,channel1Ind,channel2Ind,fileChannels,excludedChannels=[],subset='all',labels=None,buff=0.02,altDir=None,centroids=None,fcsType='binary'):
    markerSize = 1
    alphaVal = 0.5

    fontName = 'arial'
    fontSize = 9
    plotType = 'png'

    colors = get_all_colors()

    ## prepare figure
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(111)
    ax.clear()

    ## specify channels
    index1 = int(channel1Ind)
    index2 = int(channel2Ind)
    
    channel1 = fileChannels[index1]
    channel2 = fileChannels[index2]

    ## exclude scatter
    if fcsType == 'binary':
        data = pyfcm_load_fcs_file(filePath)
        fileChannels = data.channels
    elif fcsType == 'text':
        data = read_txt_into_array(filePath)
        fileChannels = read_txt_to_file_channels(filePath)
    else:
        print "ERROR: invalid fcs data type"

    ## specify data
    if len(excludedChannels) > 0:
        includedChannels = list(set(range(len(fileChannels))).difference(set(excludedChannels)))
    else:
        includedChannels = range(len(fileChannels))

    if len(excludedChannels) != 0:
        includedChannels = list(set(range(len(fileChannels))).difference(set(excludedChannels)))
        includedChannelLabels = np.array(fileChannels)[includedChannels].tolist()
        excludedChannelLabels = np.array(fileChannels)[excludedChannels].tolist()
    else:
        includedChannels = range(len(fileChannels))
        includedChannelLabels = fileChannels
        excludedChannelLabels = []

    data = data[:,includedChannels]
    fileChannels = np.array(fileChannels)[includedChannels]

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
            try:
                selectedColor = colors[l]
            except:
                print 'WARNING not enough colors in self.colors looking for ', l
                clustColor = 'black'

            clustCount += 1

            x = data[:,index1][np.where(labels==l)[0]]
            y = data[:,index2][np.where(labels==l)[0]]
            
            totalPoints+=x.size

            if x.size == 0:
                continue
            ax.scatter(x,y,color=selectedColor,s=markerSize)

            ## handle centroids if present
            prefix = ''
            if centroids != None:
                xPos = centroids[l][index1] # str(l)
                yPos = centroids[l][index2] # str(l)

                if selectedColor in ['#FFFFAA','y']:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=selectedColor)
                            )
                else:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white',
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=selectedColor)
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
'''

def make_plots_as_subplots(expListNames,expListDataPaths,expListLabels,colInd1=0,colInd2=1,centroids=None,colInd1Name=None, colInd2Name=None,
                           showCentroids=True,figTitle=None,markerSize=1,saveas=None,subplotRows=3,subplotCols=2,refFile=None, covariateList=[],
                           dataType='fcs',subsample=None,highlight=None,excludedChannels=[],fontSize=10,asData=False,fontName='arial'):

    if subplotRows > subplotCols:
        fig = plt.figure(figsize=(6.5,9))
    elif subplotCols > subplotRows:
        fig = plt.figure(figsize=(10,7))
    else:
        fig = plt.figure(figsize=(9,8))

    ## error checking
    if len(expListNames) != len(expListDataPaths) or len(expListNames) != len(expListLabels):
        print "ERROR: cannot make_plots_as_subplots - bad input data",
        print len(expListNames), len(expListDataPaths), len(expListLabels)
        return 
    
    subplotCount = 0
    colors = get_all_colors()

    ## handle subsetting
    if subsample != None:
        numObs = None
        minNumObs = np.inf
        
        # get minimum number of observations out of all files considered 
        for filePath in expListDataPaths:
            if asData == False:
                expData, fChannels = get_file_data(filePath,dataType)
            else:
                expData = filePath
            n,d = np.shape(expData)
        
            if n < minNumObs:
                minNumObs = n

        subsampleIndices = np.random.random_integers(0,minNumObs-1,subsample)
    else:
        subsampleIndices = None
        
    ## determin the ymax and xmax
    xMaxList, yMaxList, xMinList, yMinList = [],[],[],[]
    for c in range(len(expListNames)):
        if asData == False:
            expData,fChannels = get_file_data(expListDataPaths[c],dataType)
        else:
            expData = expListDataPaths[c]

        labels = expListLabels[c]
        expName = expListNames[c]
 
        if subsampleIndices != None:
            expData = expData[subsampleIndices,:]
            labels = np.array(labels)[subsampleIndices].tolist()

        xMaxList.append(expData[:,colInd1].max())
        yMaxList.append(expData[:,colInd2].max())

        ## use only non negative numbers for min
        xMinList.append(expData[:,colInd1][np.where(expData[:,colInd1] >= 0)[0]].min())
        yMinList.append(expData[:,colInd2][np.where(expData[:,colInd2] >= 0)[0]].min())

    xAxLimit = (np.array(xMinList).min() - 0.05 * np.array(xMinList).min(), np.array(xMaxList).max() + 0.01 * np.array(xMaxList).max())
    yAxLimit = (np.array(yMinList).min() - 0.05 * np.array(yMinList).min(), np.array(yMaxList).max() + 0.01 * np.array(yMaxList).max())

    ## loop through files and create the scatter plots
    for c in range(len(expListNames)):
        if asData == False:
            expData, fChannels = get_file_data(expListDataPaths[c],dataType)
        else:
            expData = expListDataPaths[c]
        labels = expListLabels[c]
        expName = expListNames[c]

        if subsampleIndices != None:
            expData = expData[subsampleIndices,:]
            labels = np.array(labels)[subsampleIndices].tolist()

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

            ## handle highlighted clusters
            if highlight != None and str(int(highlight)) == str(int(l)):
                alphaVal = 0.8
            elif highlight !=None and str(int(highlight)) != str(int(l)):
                alphaVal = 0.5
                clustColor = "#CCCCCC"
            else:
                alphaVal=0.8

            ax.scatter(x,y,color=clustColor,s=markerSize,alpha=alphaVal)
            totalPoints+=x.size

            if highlight != None and str(int(highlight)) != str(int(l)):
                continue

            ## handle centroids if present
            prefix = ''
            if centroids != None and showCentroids == True:
                xPos = centroids[expName][str(l)][colInd1]
                yPos = centroids[expName][str(l)][colInd2]
                
                if xPos < 0 or yPos <0:
                    continue

                if clustColor in ['#FFFFAA','y','#33FF77']:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=fontSize,
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=clustColor,alpha=alphaVal)
                            )
                else:
                    ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=fontSize,
                            ha="center", va="center",
                            bbox = dict(boxstyle="round",facecolor=clustColor,alpha=alphaVal)
                            )

        ## error check that all point were plotted 
        if totalPoints != expData[:,0].size:
            print "ERROR: the correct number of point were not plotted %s/%s"%(totalPoints,expData[:,0].size)

        if expListNames[subplotCount-1] == refFile:
            fontWeight = 'heavy'
        else:
            fontWeight = 'normal'

        fileName = expListNames[subplotCount-1]
        fileName = re.sub("ACS\-T\-Pt\_","",fileName)
        print fileName

        if len(covariateList) > 0:
            subplotTitle = fileName +"-"+covariateList[subplotCount-1]
        else:
            subplotTitle = fileName
        
        ax.set_title(subplotTitle,fontsize=fontSize,fontweight=fontWeight)

        ax.set_xlim([xAxLimit[0],xAxLimit[1]])
        ax.set_ylim([yAxLimit[0],yAxLimit[1]])

        ax.xaxis.set_major_locator(MaxNLocator(4))
        ax.yaxis.set_major_locator(MaxNLocator(4))

        lastFew = len(expListNames) % subplotCols
        if lastFew == 0:
            lastFew = subplotCols
        leftSidePanels = np.arange(1,subplotCols*subplotRows+1,subplotCols)
        bottomPanels = np.arange(1,subplotCols*subplotRows+1)[-lastFew:].tolist() + [len(expListNames)-1]

        ## format ticklabels
        xticklabels = plt.getp(plt.gca(), 'xticklabels')
        plt.setp(xticklabels, fontsize=fontSize-1, fontname=fontName)
        yticklabels = plt.getp(plt.gca(), 'yticklabels')
        plt.setp(yticklabels, fontsize=fontSize-1, fontname=fontName)


        if subplotCount not in leftSidePanels:
            ax.set_yticks([])
        else:
            if colInd2Name != None:
                ax.set_ylabel(colInd2Name,fontsize=fontSize-1,fontname=fontName)

        if subplotCount not in bottomPanels:
            ax.set_xticks([])
        else:
            if colInd1Name != None:
                ax.set_xlabel(colInd1Name,fontsize=fontSize-1,fontname=fontName)

        if figTitle != None:
            fig.suptitle(figTitle, fontsize=fontSize, fontname=fontName)

        plt.subplots_adjust(wspace=0.1, hspace=0.2)

        if saveas != None:
            fig.savefig(saveas,dpi=300)



    def makePlotsSameAxis(self,expListNames,expListData,expListLabels,colors,centroids,showCentroids=True):
        fig = plt.figure(figsize=(7,7))
        ax = fig.add_subplot(111)
        plotCount = -1
        plotMarkers = ["o","+","^","s"]
        plotDict = {}

        for c in range(len(expListNames)):
            plotCount += 1
            expData = expListData[c]
            labels = expListLabels[c]
            expName = expListNames[c]

            if plotCount == 0:
                visible = True
            else:
                visible = False

            x = expData[:,0]
            y = expData[:,1]

            plotDict[plotCount] = ax.scatter(x,y,color=colors[plotCount],s=self.markerSize,visible=visible)
            #ax.set_title("Case %s"%subplotCount) 
 
            ax.set_xlim([0,14])
            ax.set_ylim([0,14])

        rax = plt.axes([0.15, 0.12, 0.15, 0.15])
        check = CheckButtons(rax, ('Case1', 'Case2', 'Case3','Case4'), (True, False, False, False))

        def func(label):
            if label == 'Case1': plotDict[0].set_visible(not plotDict[0].get_visible())
            elif label == 'Case2': plotDict[1].set_visible(not plotDict[1].get_visible())
            elif label == 'Case3': plotDict[2].set_visible(not plotDict[2].get_visible())
            elif label == 'Case4': plotDict[3].set_visible(not plotDict[3].get_visible())
            plt.draw()
        check.on_clicked(func)
