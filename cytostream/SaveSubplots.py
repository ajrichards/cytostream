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
from cytostream import Model, Logger, get_fcs_file_names
from cytostream.tools import get_all_colors, get_file_sample_stats, get_file_data, draw_plot

class SaveSubplots():
    def __init__(self, controller, channelDict, figName, numSubplots,mainWindow=None,plotType='scatter',figMode='qa',
                 figTitle=None,useSimple=False,useScale=False,inputLabels=None,drawState='heat',
                 minNumEvents=3,subplotTitle=False,addLine=None,figSize=None,axesOff=False,subsample='original'):

        ## arg variables
        self.controller = controller
        self.channelDict = channelDict
        self.numSubplots = numSubplots
        self.mainWindow = mainWindow
        self.figMode = figMode
        self.figTitle = figTitle
        self.figName = figName
        self.plotType = plotType
        self.buff = 0.02
        self.useScale = useScale
        self.useSimple = useSimple
        self.inputLabels = None
        self.fontName = 'Ariel'
        self.drawState = drawState
        self.minNumEvents = minNumEvents
        self.subplotTitle = subplotTitle
        self.addLine = addLine
        self.figSize = figSize
        self.axesOff = axesOff
        self.subsample = subsample
        self.resultsMode = 'components'

        ## error check
        run = True
        print type(self.controller)
        if os.path.isdir(homeDir) == False:
            print "ERROR: SaveSubplots.py -- homedir does not exist -- bad project name", projectID, homeDir
            run = False
        if run == True:
            self.log = self.controller.log
            self.model = self.controller.model

        ## other variables
        self.fileNameList = self.controller.fileNameList 
        self.homeDir = controller.homeDir
        self.channelList = self.log.log['alternate_channel_labels']

        if inputLabels != None:
            self.inputLabels = []
            for labelList in inputLabels:
                self.inputLabels.append(np.array([i for i in labelList]))

        if self.figMode not in ['qa','analysis']:
            print "ERROR: SaveSubplots.py -- figMode  must be 'qa' or 'analysis' not '%s'"%self.figMode

        ## initialize a logger and a model to get specified files and channels
            #self.log.initialize(self.homeDir,load=True)
            #self.model = Model()
            #self.model.initialize(self.homeDir)
            #self.fontName = self.log.log['font_name']
            #self.filterInFocus = self.log.log['filter_in_focus']
            #self.resultsMode = self.log.log['results_mode']
        
        ## prepare figure
        if self.figSize == None:
            self.fig = plt.figure()
        else:
            self.fig = plt.figure(figsize=self.figSize)

        self.colors = get_all_colors()

        #if self.forceScale == True:
        #    self.handle_axes_limits()
        #    self.forceScale = (self.xAxLimit,self.yAxLimit)
        #else:
        #    self.forceScale = False

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
            dpi = 100
        elif self.numSubplots in [3]:
            self.fig.subplots_adjust(wspace=0.32)
            dpi = 110
        elif self.numSubplots in [4]:
            self.fig.subplots_adjust(hspace=0.25,wspace=0.005)
            dpi = 120
        elif self.numSubplots in [5,6]:
            self.fig.subplots_adjust(hspace=0.05,wspace=0.3)
            dpi = 130
        elif self.numSubplots in [7,8,9]:
            self.fig.subplots_adjust(hspace=0.3,wspace=0.05)
            dpi = 140
        elif self.numSubplots in [10,11,12]:
            self.fig.subplots_adjust(hspace=0.2,wspace=0.4)
            dpi = 150
        elif self.numSubplots in [13,14,15,16]:
            self.fig.subplots_adjust(hspace=0.2,wspace=0.4)
            dpi = 160

        self.fig.savefig(self.figName,transparent=False,dpi=dpi)
                             
    def generic_callback():
        print "generic callback"

    def make_plots(self):
        ## declare variables
        plotsToViewChannels     = self.log.log['plots_to_view_channels']
        plotsToViewFiles        = self.log.log['plots_to_view_files']
        plotsToViewRuns         = self.log.log['plots_to_view_runs']
        plotsToViewHighlights   = self.log.log['plots_to_view_highlights']

        if len(plotsToViewChannels) != len(plotsToViewFiles):
            print "ERROR: SaveSubplots -- failed error check 1 make_scatter_plots",len(plotsToViewChannels),len(plotsToViewFiles)
        if len(plotsToViewChannels) != len(plotsToViewRuns):
            print "ERROR: SaveSubplots -- failed error check 2 make_scatter_plots",len(plotsToViewChannels),len(plotsToViewRuns)
        if len(plotsToViewChannels) < self.numSubplots:
            print "ERROR: SaveSubplots -- failed error check 3 make_scatter_plots"

        ## get subsample
        #if self.figMode == 'qa':
        #    self.subsample = self.log.log['subsample_qa'] 
        #    labels = None
        #else:
        #    self.subsample = self.log.log['subsample_analysis']

        ## loop through all subplots
        for subplotIndex in range(self.numSubplots):
            subplotFile = self.fileNameList[int(plotsToViewFiles[int(subplotIndex)])]
            subplotChannels = plotsToViewChannels[int(subplotIndex)]
            subplotRunID = plotsToViewRuns[int(subplotIndex)]
            subplotHighlight = plotsToViewHighlights[int(subplotIndex)]

            if self.figMode == 'qa':
                pass
            elif self.figMode == 'analysis' and self.inputLabels != None:
                labels = self.inputLabels[subplotIndex]
            elif self.figMode == 'analysis':
                statModel, statModelClasses = self.model.load_model_results_pickle(subplotFile,subplotRunID,modelType=self.resultsMode)
                labels = statModelClasses
                modelLog = self.model.load_model_results_log(subplotFile,subplotRunID)
                self.subsample = modelLog['subsample']
            else:
                print "WARNING: unexpected event occured in SaveSubplots.py", self.figMode

            ## get original events and labels for draw_plot
            events = self.controller.get_events(subplotFile,'original')
            labels = self.controller.get_labels(subplotFile,subplotRunID,subsample='original')

            print events.shape
            print labels.shape

            ## give draw plot an array for subsample
            if type(np.array([])) == type(self.subsample):
                pass
            elif self.subsample != 'original' and self.subsample != None:
                key = str(int(float(self.subsample)))
                self.controller.handle_subsampling(self.subsample)
                self.subsample = self.controller.subsampleDict[key]

            index1,index2 = subplotChannels

            ## labels
            if self.subplotTitle == True:
                subplotTitle = subplotFile
            else:
                subplotTitle = None
            
            axesLabels = (None,None)
            showNoise = False

            ## labels
            #if self.figMode == 'analysis':
            #    self.controller.labels_load(subplotRunID,modelType=self.resultsMode)
            #    labelsList = self.controller.labelsList[subplotRunID]
            #else:
            #    labelsList == None

            ## handle args
            args = [None for i in range(18)]
            args[0] = self.get_axes(subplotIndex)
            args[1] = events
            args[2] = self.channelList
            args[3] = self.channelDict
            args[4] = index1
            args[5] = index2
            args[6] = self.subsample
            args[7] = self.log.log['selected_transform']
            args[8] = labels
            args[9] = subplotHighlight
            args[10] = self.log.log
            args[11] = self.drawState
            args[12] = self.numSubplots
            args[13] = axesLabels
            args[14] = self.subplotTitle
            args[15] = showNoise
            args[16] = self.useSimple
            args[17] = self.useScale

            ## add a line if specified {subplot:(lineX,lineY)}
            if self.addLine != None and subplotIndex in self.addLine.keys():
                draw_plot(args,addLine=self.addLine[subplotIndex],axesOff=self.axesOff)
            else:
                draw_plot(args,axesOff=self.axesOff)

    #def handle_axes_limits(self):
    #
    #    ## fetch plot variables
    #    fileChannels = self.log.log['alternate_channel_labels']
    #    fileList = get_fcs_file_names(self.homeDir)
    #    plotsToViewChannels       = self.log.log['plots_to_view_channels']
    #    plotsToViewFiles          = self.log.log['plots_to_view_files']
    #    plotsToViewRuns           = self.log.log['plots_to_view_runs']
    #    plotsToViewHighlights     = self.log.log['plots_to_view_highlights']
    #    subsample = self.log.log['subsample_qa'] 
    #    labels = None##
    #
    #    xMaxList, yMaxList, xMinList, yMinList = [],[],[],[]
    #    for subplotIndex in range(self.numSubplots):
    #        subplotFile = fileList[int(plotsToViewFiles[int(subplotIndex)])]
    #        subplotChannels = plotsToViewChannels[int(subplotIndex)]
    #        subplotRun = plotsToViewRuns[int(subplotIndex)]
    #        subplotHighlight = plotsToViewHighlights[int(subplotIndex)]
    #    
    #        if self.figMode != 'qa' and self.inputLabels == None:
    #            statModel, statModelClasses = self.model.load_model_results_pickle(subplotFile,subplotRun,modelType=self.resultsMode)
    #            labels = statModelClasses
    #            modelLog = self.model.load_model_results_log(subplotFile,subplotRun)
    #            subsample = modelLog['subsample']
    #        elif self.inputLabels != None:
    #            subsample = self.log.log['subsample_analysis']
    #
    #        ## determine min and max numbers
    #        events,labels = fetch_plotting_events(subplotFile,self.model,self.log,subsample,labels=labels)
    #        xMaxList.append(events[:,subplotChannels[0]].max())
    #        yMaxList.append(events[:,subplotChannels[1]].max())
    #
    #        ## use only non negative numbers for min
    #        xMinList.append(events[:,subplotChannels[0]][np.where(events[:,subplotChannels[0]] >= 0)[0]].min())
    #        yMinList.append(events[:,subplotChannels[1]][np.where(events[:,subplotChannels[1]] >= 0)[0]].min())
    #
    #    self.xAxLimit = (np.array(xMinList).min() - 0.05 * np.array(xMinList).min(), np.array(xMaxList).max() + 0.01 * np.array(xMaxList).max())
    #    self.yAxLimit = (np.array(yMinList).min() - 0.05 * np.array(yMinList).min(), np.array(yMaxList).max() + 0.01 * np.array(yMaxList).max())

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
    channelDict = {'fsc-h':0,'ssc-h':1} 
    figName = os.path.join(os.getenv("HOME"),'test')

    if os.path.exists(run1File) == False:
        print "utest model run was not found.....running"
        filePathList = [os.path.join(".","example_data","3FITC_4PE_004.fcs")]
        nga = NoGuiAnalysis(homeDir,channelDict,filePathList,channelDict,useSubsample=True,makeQaFigs=False,record=False,verbose=False)
        nga.run_model()
    else:
        nga = NoGuiAnalysis(os.path.join(homeDir),channelDict,loadExisting=True)

    figMode = 'analysis'
    numSubplots = 12
    ss = SaveSubplots(nga.controller,channelDict,figName,numSubplots,figMode=figMode,figTitle='Example title',useScale=True)
    print 'plot saved as ', figName
