#!/usr/bin/python
'''
Cytostream
SaveImagesCenter
The a transition widget to detail the creating and saving of images

'''

__author__ = "A Richards"

import sys,time,os,re
from PyQt4 import QtGui, QtCore
import numpy as np
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

import matplotlib.pyplot as plt
from cytostream import Logger, Model, get_fcs_file_names
from cytostream import NoGuiAnalysis
from cytostream.tools import get_all_colors, fetch_plotting_events, get_file_sample_stats, get_file_data
from fcm.graphics import bilinear_interpolate

class SaveSubplots():
    def __init__(self, homeDir, figName, numSubplots,mainWindow=None,plotType='scatter',figMode='qa',figTitle=None,
                 forceScale=False,fontSize=8,markerSize=1,dpi=200,inputLabels=None,drawState='Heat',showOnlyClusters=None):

        ## arg variables
        self.homeDir = homeDir
        self.numSubplots = numSubplots
        self.mainWindow = mainWindow
        self.figMode = figMode
        self.figTitle = figTitle
        self.figName = figName
        self.plotType = plotType
        self.buff = 0.02
        self.dpi = dpi
        self.fontSize = fontSize
        self.markerSize = markerSize
        self.forceScale = forceScale
        self.inputLabels = None
        self.fontName = 'ariel'
        self.drawState = drawState
        self.showOnlyClusters = showOnlyClusters

        ## error check
        run = True
        if os.path.isdir(homeDir) == False:
            print "ERROR: SaveSubplots.py -- homedir does not exist -- bad project name", projectID, homeDir
            run = False

        if inputLabels != None:
            self.inputLabels = []
            for labelList in inputLabels:
                self.inputLabels.append(np.array([i for i in labelList]))

        ## initialize a logger and a model to get specified files and channels
        if run == True:
            self.log = Logger()
            self.log.initialize(self.homeDir,load=True)
            self.model = Model()
            self.model.initialize(self.homeDir)
            self.fontName = self.log.log['font_name']
            self.filterInFocus = self.log.log['filter_in_focus']
            self.resultsMode = self.log.log['results_mode']
        
            ## prepare figure
            self.fig = plt.figure()
            self.colors = get_all_colors()

            if self.forceScale == True:
                self.handle_axes_limits()

            if self.plotType == 'scatter':
                self.make_plots()
            else:
                print 'ERROR: SaveSubplots.py: plotType not implemented', self.plotType
                return None

        ## save file
        if self.figTitle != None:
            plt.suptitle(self.figTitle,fontsize=self.fontSize+2, fontname=self.fontName)
            
        if self.numSubplots in [2]:
            self.fig.subplots_adjust(wspace=0.2)
        elif self.numSubplots in [3]:
            self.fig.subplots_adjust(wspace=0.3)
        elif self.numSubplots in [4]:
            self.fig.subplots_adjust(hspace=0.2,wspace=0.05)
        elif self.numSubplots in [5,6]:
            self.fig.subplots_adjust(hspace=0.05,wspace=0.3)
        elif self.numSubplots in [7,8,9]:
            self.fig.subplots_adjust(hspace=0.3,wspace=0.05)
        elif self.numSubplots in [10,11,12]:
            self.fig.subplots_adjust(hspace=0.2,wspace=0.4)
            
        self.fig.savefig(self.figName,transparent=False,dpi=self.dpi)
                             
    def generic_callback():
        print "generic callback"

    def make_plots(self):
        ## declare variables     
        plotsToViewChannels       = self.log.log['plots_to_view_channels']
        plotsToViewFiles          = self.log.log['plots_to_view_files']
        plotsToViewRuns           = self.log.log['plots_to_view_runs']
        plotsToViewHighlights     = self.log.log['plots_to_view_highlights']

        if len(plotsToViewChannels) != len(plotsToViewFiles):
            print "ERROR: SaveSubplotsCenter -- failed error check 1 make_scatter_plots",len(plotsToViewChannels),len(plotsToViewFiles)
        if len(plotsToViewChannels) != len(plotsToViewRuns):
            print "ERROR: SaveSubplotsCenter -- failed error check 2 make_scatter_plots",len(plotsToViewChannels),len(plotsToViewRuns)
        if len(plotsToViewChannels) < self.numSubplots:
            print "ERROR: SaveSubplotsCenter -- failed error check 3 make_scatter_plots"

        ## get subsample
        if self.figMode == 'qa':
            subsample = self.log.log['subsample_qa'] 
            labels = None
        else:
            subsample = self.log.log['subsample_analysis']

        ## fetch plot variables
        fileChannels = self.log.log['alternate_channel_labels']
        fileList = get_fcs_file_names(self.homeDir)

        ## loop through all subplots
        for subplotIndex in range(self.numSubplots):
            subplotFile = fileList[int(plotsToViewFiles[int(subplotIndex)])]
            subplotChannels = plotsToViewChannels[int(subplotIndex)]
            subplotRun = plotsToViewRuns[int(subplotIndex)]
            subplotHighlight = plotsToViewHighlights[int(subplotIndex)]

            if self.figMode != 'qa' and self.inputLabels != None:
                labels = self.inputLabels[subplotIndex]
            elif self.figMode != 'qa':
                statModel, statModelClasses = self.model.load_model_results_pickle(subplotFile,subplotRun,modelType=self.resultsMode)
                labels = statModelClasses
                modelLog = self.model.load_model_results_log(subplotFile,subplotRun)
                subsample = modelLog['subsample']

            events,labels = fetch_plotting_events(subplotFile,self.model,self.log,subsample,labels=labels)
            index1,index2 = subplotChannels

            if self.drawState.lower() == 'scatter':
                self._make_scatter_scatter(events,labels,fileChannels,index1,index2,subplotIndex,highlight=subplotHighlight)
            elif self.drawState.lower() == 'heat':
                self._make_scatter_heat(events,labels,fileChannels,index1,index2,subplotIndex,highlight=subplotHighlight)

    def _make_scatter_scatter(self,events,labels,fileChannels,index1,index2,subplotIndex,highlight=None):
        
        ## error checking
        if labels != None:
            n,d = events.shape
            if n != labels.size:
                print "ERROR: SaveSubplotsCenter.py -- _make_scatter_plots -- labels and events do not match",n,labels.size
                return None

        if highlight == "None":
            highlight = None

        ## figure variables
        ax = self.get_axes(subplotIndex)

        ## handle centroids
        if labels != None:
            centroids,variances,sizes = get_file_sample_stats(events,labels)

        ## error check
        if labels != None and  np.unique(labels).size > len(self.colors):
            print "WARNING: lots of labels adding more colors"
            self.colors = self.colors*6
            print "DEBUG SaveSubPlots: ", np.unique(labels).size, len(self.colors)

        ## make plot
        totalPoints = 0

        if labels == None:
            ax.scatter([events[:,index1]],[events[:,index2]],color='blue',s=self.markerSize,edgecolor='none')
        else:
            if type(np.array([])) != type(labels):
                labels = np.array(labels)

            numLabels = np.unique(labels).size
            maxLabel = np.max(labels)
            
            for l in np.sort(np.unique(labels)):
                if l == -1:
                    clusterColor = "#C0C0C0"
                    marker = '+'
                else:
                    clusterColor = self.colors[l]
                    marker = "o"
                ms = self.markerSize

                if self.showOnlyClusters != None and l not in self.showOnlyClusters:
                    continue

                ## handle highlighted clusters
                if highlight != None and str(int(highlight)) == str(int(l)):
                    alphaVal = 0.8
                    ms = ms+4
                elif highlight !=None and str(int(highlight)) != str(int(l)):
                    alphaVal = 0.5
                    clusterColor = "#CCCCCC"
                else:
                    alphaVal=0.8

                x = events[:,index1][np.where(labels==l)[0]]
                y = events[:,index2][np.where(labels==l)[0]]

                totalPoints+=x.size

                if x.size == 0:
                    continue
                ax.scatter(x,y,color=clusterColor,s=ms,edgecolor='none',marker='o')
                
                ## handle centroids if present
                prefix = ''

                if centroids != None:
                    if centroids[str(int(l))].size != events.shape[1]:
                        print "ERROR: ScatterPlotter.py -- centroids not same shape as events"

                    xPos = centroids[str(int(l))][index1]
                    yPos = centroids[str(int(l))][index2]

                    if xPos < 0 or yPos <0:
                        continue
                    labelSize = self.fontSize
                    if self.numSubplots == 12:
                        labelSize = 4
                        
                    if clusterColor in ['#FFFFAA','y','#33FF77']:
                        ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=labelSize,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                )
                    elif clusterColor == "#C0C0C0":
                        ax.text(xPos, yPos, '%s%s'%(prefix,l), color='blue',fontsize=labelSize,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                )
                    else:
                        ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=labelSize,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                )
        
        ## handle data edge buffers     
        bufferX = self.buff * (events[:,index1].max() - events[:,index1].min())
        bufferY = self.buff * (events[:,index2].max() - events[:,index2].min())
        ax.set_xlim([events[:,index1].min()-bufferX,events[:,index1].max()+bufferX])
        ax.set_ylim([events[:,index2].min()-bufferY,events[:,index2].max()+bufferY])

        ## handle labels and title
        channel1 = fileChannels[index1]
        channel2 = fileChannels[index2]
        ax.set_xlabel(channel1,fontname=self.fontName,fontsize=self.fontSize)
        ax.set_ylabel(channel2,fontname=self.fontName,fontsize=self.fontSize)
        xticklabels = plt.getp(plt.gca(),'xticklabels')
        yticklabels = plt.getp(plt.gca(),'yticklabels')
        plt.setp(xticklabels,fontsize=self.fontSize-1, fontname = self.fontName)
        plt.setp(yticklabels,fontsize=self.fontSize-1, fontname = self.fontName)
        
        if self.forceScale == True:
            ax.set_xlim(self.xAxLimit)
            ax.set_ylim(self.yAxLimit)
        
        ax.set_aspect(1./ax.get_data_ratio())

    def _make_scatter_heat(self,events,labels,fileChannels,index1,index2,subplotIndex,highlight=None):
        
        ## error checking
        if labels != None:
            n,d = events.shape
            if n != labels.size:
                print "ERROR: SaveSubplotsCenter.py -- _make_scatter_plots -- labels and events do not match",n,labels.size
                return None

        if highlight == "None":
            highlight = None

        ## figure variables
        ax = self.get_axes(subplotIndex)

        ## handle centroids
        if labels != None:
            centroids,variances,sizes = get_file_sample_stats(events,labels)

        ## error check
        if labels != None and  np.unique(labels).size > len(self.colors):
            print "WARNING: lots of labels adding more colors"
            self.colors = self.colors*6
            print "DEBUG SaveSubPlots: ", np.unique(labels).size, len(self.colors)

        x,y = (events[:,index1],events[:,index2])

        ## axes buffering
        #bufferX = buff * (x.max() - x.min())
        #bufferY = buff * (y.max() - y.min())
        #xMin, xMax = x.min()-bufferX,x.max()+bufferX
        #yMin, yMax = y.min()-bufferY,y.max()+bufferY

        myCmap = mpl.cm.gist_heat
        totalPts = len(x)
        if totalPts >= 9e04:
            bins = 120.0
        elif totalPts >= 5e04:
            bins = 50.0
        else:
            bins = 40.0

        colorList = bilinear_interpolate(x,y,bins=bins)

        ## make plot
        totalPoints = 0
        
        if str(labels) == None:
            ax.scatter(x,y,c=colorList,s=1,edgecolors='none',cmap=myCmap)
        else:
            if type(np.array([])) != type(labels):
                labels = np.array(labels)

            numLabels = np.unique(labels).size
            maxLabel = np.max(labels)
            
            for l in np.sort(np.unique(labels)):
                if l == -1:
                    clusterColor = "#C0C0C0"
                    marker = '+'
                else:
                    clusterColor = self.colors[l]
                    marker = "o"

                if self.showOnlyClusters != None and l not in self.showOnlyClusters:
                    continue

                markerSize = self.markerSize
                clusterInds = np.where(labels==l)[0]
                dataX = events[:,index1][clusterInds]
                dataY = events[:,index2][clusterInds]

                ## handle highlighted clusters
                if highlight != None and str(int(highlight)) == str(int(l)):
                    alphaVal = 0.8
                    ms = ms+4
                elif highlight !=None and str(int(highlight)) != str(int(l)):
                    alphaVal = 0.5
                    clusterColor = "#CCCCCC"
                else:
                    alphaVal=0.8

                totalPoints+=x.size
                if dataX.size == 0:
                    continue
         
                clrs = colorList[clusterInds]
                ax.scatter(dataX,dataY,c=clrs,s=markerSize,edgecolor='none',cmap=myCmap)
                
                ## handle centroids if present
                prefix = ''

                if centroids != None:
                    if centroids[str(int(l))].size != events.shape[1]:
                        print "ERROR: ScatterPlotter.py -- centroids not same shape as events"

                    xPos = centroids[str(int(l))][index1]
                    yPos = centroids[str(int(l))][index2]

                    if xPos < 0 or yPos <0:
                        continue
                    labelSize = self.fontSize
                    if self.numSubplots == 12:
                        labelSize = 4
                        
                    if clusterColor in ['#FFFFAA','y','#33FF77']:
                        ax.text(xPos, yPos, '%s%s'%(prefix,l), color='black',fontsize=labelSize-2,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                )
                    elif clusterColor == "#C0C0C0":
                        ax.text(xPos, yPos, '%s%s'%(prefix,l), color='blue',fontsize=labelSize-2,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                )
                    else:
                        ax.text(xPos, yPos, '%s%s'%(prefix,l), color='white', fontsize=labelSize-2,
                                ha="center", va="center",
                                bbox = dict(boxstyle="round",facecolor=clusterColor,alpha=alphaVal)
                                )
        
        ## handle data edge buffers     
        bufferX = self.buff * (events[:,index1].max() - events[:,index1].min())
        bufferY = self.buff * (events[:,index2].max() - events[:,index2].min())
        ax.set_xlim([events[:,index1].min()-bufferX,events[:,index1].max()+bufferX])
        ax.set_ylim([events[:,index2].min()-bufferY,events[:,index2].max()+bufferY])

        ## handle labels and title
        channel1 = fileChannels[index1]
        channel2 = fileChannels[index2]
        ax.set_xlabel(channel1,fontname=self.fontName,fontsize=self.fontSize)
        ax.set_ylabel(channel2,fontname=self.fontName,fontsize=self.fontSize)
        xticklabels = plt.getp(plt.gca(),'xticklabels')
        yticklabels = plt.getp(plt.gca(),'yticklabels')
        plt.setp(xticklabels, fontsize=self.fontSize-1, fontname = self.fontName)
        plt.setp(yticklabels, fontsize=self.fontSize-1, fontname = self.fontName)
        
        if self.forceScale == True:
            print "DBG: SaveSubplots using forceScale"
            ax.set_xlim(self.xAxLimit)
            ax.set_ylim(self.yAxLimit)
        
        ax.set_aspect(1./ax.get_data_ratio())

    def handle_axes_limits(self):

        ## fetch plot variables
        fileChannels = self.log.log['alternate_channel_labels']
        fileList = get_fcs_file_names(self.homeDir)
        plotsToViewChannels       = self.log.log['plots_to_view_channels']
        plotsToViewFiles          = self.log.log['plots_to_view_files']
        plotsToViewRuns           = self.log.log['plots_to_view_runs']
        plotsToViewHighlights     = self.log.log['plots_to_view_highlights']
        subsample = self.log.log['subsample_qa'] 
        labels = None

        xMaxList, yMaxList, xMinList, yMinList = [],[],[],[]
        for subplotIndex in range(self.numSubplots):
            subplotFile = fileList[int(plotsToViewFiles[int(subplotIndex)])]
            subplotChannels = plotsToViewChannels[int(subplotIndex)]
            subplotRun = plotsToViewRuns[int(subplotIndex)]
            subplotHighlight = plotsToViewHighlights[int(subplotIndex)]
        
            if self.figMode != 'qa' and self.inputLabels == None:
                statModel, statModelClasses = self.model.load_model_results_pickle(subplotFile,subplotRun,modelType=self.resultsMode)
                labels = statModelClasses
                modelLog = self.model.load_model_results_log(subplotFile,subplotRun)
                subsample = modelLog['subsample']
            elif self.inputLabels != None:
                subsample = self.log.log['subsample_analysis']

            ## determine min and max numbers
            events,labels = fetch_plotting_events(subplotFile,self.model,self.log,subsample,labels=labels)
            xMaxList.append(events[:,subplotChannels[0]].max())
            yMaxList.append(events[:,subplotChannels[1]].max())

            ## use only non negative numbers for min
            xMinList.append(events[:,subplotChannels[0]][np.where(events[:,subplotChannels[0]] >= 0)[0]].min())
            yMinList.append(events[:,subplotChannels[1]][np.where(events[:,subplotChannels[1]] >= 0)[0]].min())

        self.xAxLimit = (np.array(xMinList).min() - 0.05 * np.array(xMinList).min(), np.array(xMaxList).max() + 0.01 * np.array(xMaxList).max())
        self.yAxLimit = (np.array(yMinList).min() - 0.05 * np.array(yMinList).min(), np.array(yMaxList).max() + 0.01 * np.array(yMaxList).max())

    def get_axes(self,subplotIndex):
        if self.numSubplots == 1:
            ax = self.fig.add_subplot(1,1,subplotIndex+1)
        elif self.numSubplots == 2:
            ax = self.fig.add_subplot(1,2,subplotIndex+1)
        elif self.numSubplots == 3:
            ax = self.fig.add_subplot(1,3,subplotIndex+1)
        elif self.numSubplots == 4:
            ax = self.fig.add_subplot(2,2,subplotIndex+1)
        elif self.numSubplots == 5:
            ax = self.fig.add_subplot(2,3,subplotIndex+1)
        elif self.numSubplots == 6:
            ax = self.fig.add_subplot(2,3,subplotIndex+1)
        elif self.numSubplots == 7:
            ax = self.fig.add_subplot(3,3,subplotIndex+1)
        elif self.numSubplots == 8:
            ax = self.fig.add_subplot(3,3,subplotIndex+1)
        elif self.numSubplots == 9:
            ax = self.fig.add_subplot(3,3,subplotIndex+1)
        elif self.numSubplots == 10:
            ax = self.fig.add_subplot(3,4,subplotIndex+1)
        elif self.numSubplots == 11:
            ax = self.fig.add_subplot(3,4,subplotIndex+1)
        elif self.numSubplots == 12:
            ax = self.fig.add_subplot(3,4,subplotIndex+1)

        return ax

### Run the tests 
if __name__ == '__main__':
    ''' 
    Note: to show the opening screen set fileList = [] 
          otherwise use fileList = ['3FITC_4PE_004']
    
    '''
    
    homeDir = os.path.join("projects","utest")
    run1File = os.path.join("projects","utest","models","3FITC_4PE_004_run1_modes.pickle")
    figName = os.path.join(os.getenv("HOME"),'test')

    if os.path.exists(run1File) == False:
        print "utest model run was not found.....running"
        filePathList = [os.path.join(".","example_data","3FITC_4PE_004.fcs")]
        nga = NoGuiAnalysis(homeDir,filePathList,useSubsample=True,makeQaFigs=False,record=False,verbose=False)

    #else:
    figMode = 'analysis'
    numSubplots = 12
    ss = SaveSubplots(homeDir,figName,numSubplots,figMode=figMode,figTitle='Example title',forceScale=True)
    print 'plot saved as ', figName
