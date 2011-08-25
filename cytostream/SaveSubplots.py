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
from cytostream.tools import get_all_colors, fetch_plotting_events, get_file_sample_stats, get_file_data, draw_plot

class SaveSubplots():
    def __init__(self, homeDir, figName, numSubplots,mainWindow=None,plotType='scatter',figMode='qa',
                 figTitle=None,forceSimple=False,forceScale=False,inputLabels=None,drawState='Heat',
                 minNumEvents=3,useSubplotTitles=True,addLine=None,figSize=None):

        ## arg variables
        self.homeDir = homeDir
        self.numSubplots = numSubplots
        self.mainWindow = mainWindow
        self.figMode = figMode
        self.figTitle = figTitle
        self.figName = figName
        self.plotType = plotType
        self.buff = 0.02
        self.forceScale = forceScale
        self.forceSimple = forceSimple
        self.inputLabels = None
        self.fontName = 'ariel'
        self.drawState = drawState
        self.minNumEvents = minNumEvents
        self.useSubplotTitles = useSubplotTitles
        self.addLine = addLine
        self.figSize = figSize

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
            if self.figSize == None:
                self.fig = plt.figure()
            else:
                self.fig = plt.figure(figsize=self.figSize)

            self.colors = get_all_colors()

            if self.forceScale == True:
                self.handle_axes_limits()
                self.forceScale = (self.xAxLimit,self.yAxLimit)
            else:
                self.forceScale = False

            if self.plotType == 'scatter':
                self.make_plots()
            else:
                print 'ERROR: SaveSubplots.py: plotType not implemented', self.plotType
                return None
        
        ## save file
        if self.figTitle != None:
            plt.suptitle(self.figTitle,fontsize=10, fontname=self.fontName)
            
        if self.numSubplots in [1,2]:
            self.fig.subplots_adjust(wspace=0.2)
            dpi = 200
        elif self.numSubplots in [3]:
            self.fig.subplots_adjust(wspace=0.32)
            dpi = 225
        elif self.numSubplots in [4]:
            self.fig.subplots_adjust(hspace=0.25,wspace=0.005)
            dpi = 250
        elif self.numSubplots in [5,6]:
            self.fig.subplots_adjust(hspace=0.05,wspace=0.3)
            dpi = 300
        elif self.numSubplots in [7,8,9]:
            self.fig.subplots_adjust(hspace=0.3,wspace=0.05)
            dpi = 350
        elif self.numSubplots in [10,11,12]:
            self.fig.subplots_adjust(hspace=0.2,wspace=0.4)
            dpi = 400
        elif self.numSubplots in [13,14,15,16]:
            self.fig.subplots_adjust(hspace=0.2,wspace=0.4)
            dpi = 450

        self.fig.savefig(self.figName,transparent=False,dpi=dpi)
                             
    def generic_callback():
        print "generic callback"

    def make_plots(self):
        ## declare variables     
        plotsToViewChannels       = self.log.log['plots_to_view_channels']
        plotsToViewFiles          = self.log.log['plots_to_view_files']
        plotsToViewRuns           = self.log.log['plots_to_view_runs']
        plotsToViewHighlights     = self.log.log['plots_to_view_highlights']

        if len(plotsToViewChannels) != len(plotsToViewFiles):
            print "ERROR: SaveSubplots -- failed error check 1 make_scatter_plots",len(plotsToViewChannels),len(plotsToViewFiles)
        if len(plotsToViewChannels) != len(plotsToViewRuns):
            print "ERROR: SaveSubplots -- failed error check 2 make_scatter_plots",len(plotsToViewChannels),len(plotsToViewRuns)
        if len(plotsToViewChannels) < self.numSubplots:
            print "ERROR: SaveSubplots -- failed error check 3 make_scatter_plots"

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

            if self.figMode == 'analysis' and self.inputLabels != None:
                labels = self.inputLabels[subplotIndex]
            elif self.figMode == 'analysis':
                statModel, statModelClasses = self.model.load_model_results_pickle(subplotFile,subplotRun,modelType=self.resultsMode)
                labels = statModelClasses
                modelLog = self.model.load_model_results_log(subplotFile,subplotRun)
                subsample = modelLog['subsample']

            #print 'before', events.shape
            events,labels = fetch_plotting_events(subplotFile,self.model,self.log,subsample,labels=labels,
                                                  modelRunID=subplotRun)
            index1,index2 = subplotChannels

            ## labels
            if self.useSubplotTitles == True:
                subplotTitle = subplotFile
            else:
                subplotTitle = None
            
            axesLabels = (None,None)
            showNoise = False

            ## handle args
            args = [None for i in range(17)]
            args[0] = events
            args[1] = subplotFile
            args[2] = index1
            args[3] = index2
            args[4] = subsample
            args[5] = labels
            args[6] = subplotRun
            args[7] = subplotHighlight
            args[8] = self.log.log
            args[9] = self.get_axes(subplotIndex)
            args[10] = self.drawState.lower()
            args[11] = self.numSubplots
            args[12] = self.forceScale
            args[13] = axesLabels
            args[14] = subplotTitle
            args[15] = showNoise
            args[16] = self.forceSimple

            draw_plot(args)

            ## add a line if specified (subplot,(lineX,lineY))
            if self.addLine != None and self.addLine[0] == subplotIndex:
                print 'adding line'
                ax = self.get_axes(subplotIndex)
                ax.plot(self.addLine[1][0],self.addLine[1][1],color='orange',linewidth=2.5)

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
        elif self.numSubplots == 13:
            ax = self.fig.add_subplot(4,4,subplotIndex+1)
        elif self.numSubplots == 14:
            ax = self.fig.add_subplot(4,4,subplotIndex+1)
        elif self.numSubplots == 15:
            ax = self.fig.add_subplot(4,4,subplotIndex+1)
        elif self.numSubplots == 16:
            ax = self.fig.add_subplot(4,4,subplotIndex+1)

        return ax

### Run the tests 
if __name__ == '__main__':
    ''' 
    Note: to show the opening screen set fileList = [] 
          otherwise use fileList = ['3FITC_4PE_004']
    
    '''
    from cytostream import NoGuiAnalysis    
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
