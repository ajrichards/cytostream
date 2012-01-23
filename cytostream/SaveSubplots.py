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
import Controller

class SaveSubplots():
    def __init__(self,controller, figName, numSubplots,mainWindow=None,plotType='scatter',figMode='qa',
                 figTitle=None,useSimple=False,useScale=False,inputLabels=None,drawState='heat',fontName='arial',
                 minNumEvents=3,subplotTitles=None,addLine=None,figSize=None,axesOff=False,subsample='original'):

        ## arg variables
        self.controller = controller
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
        self.fontName = fontName
        self.drawState = drawState
        self.minNumEvents = minNumEvents
        self.subplotTitles = subplotTitles
        self.addLine = addLine
        self.figSize = figSize
        self.axesOff = axesOff
        self.subsample = subsample
        self.resultsMode = 'components'

        ## if given a homeDir initialize a controller
        if type(self.controller) == type('a') and os.path.exists(self.controller):
            self.controller = Controller.Controller(debug=False)
            self.controller.initialize_project(controller,loadExisting=True)
            
        ## error check
        run = True
        if os.path.isdir(self.controller.homeDir) == False:
            print "ERROR: SaveSubplots.py -- homedir does not exist -- bad project name", projectID, homeDir
            
        self.log = self.controller.log
        self.model = self.controller.model

        ## other variables
        self.fileNameList = self.controller.fileNameList 
        self.homeDir = self.controller.homeDir
        if len(self.log.log['alternate_channel_labels']) == 0:
            self.channelList = self.controller.fileChannels
        else:
            self.channelList = self.log.log['alternate_channel_labels']

        self.channelDict = self.controller.model.load_channel_dict()
        print 'channel dict', self.channelDict

        if inputLabels != None:
            self.inputLabels = []
            for labelList in inputLabels:
                self.inputLabels.append(np.array([i for i in labelList]))

        if self.figMode not in ['qa','analysis']:
            print "ERROR: SaveSubplots.py -- figMode  must be 'qa' or 'analysis' not '%s'"%self.figMode

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
            self.fig.subplots_adjust(hspace=0.4,wspace=0.2)
            dpi = 200
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
            labels = self.controller.get_labels(subplotFile,subplotRunID)
            events = self.controller.get_events(subplotFile,'original')
            
            ## ensure approproate subsample
            try:
                self.subsample = int(float(self.subsample))
            except:
                pass

            ## ensure only maximum num events are shown
            maxScatter = int(float(self.log.log['setting_max_scatter_display']))
            if self.subsample == 'original' and events.shape[0] > maxScatter:
                self.subsample = maxScatter
                subsampleIndices = self.controller.model.get_subsample_indices(self.subsample)
                if labels != None:
                    labels = labels[subsampleIndices]
            ## case where original is smaller than max scatter display
            elif self.subsample == 'original':
                subsampleIndices = np.arange(events.shape[0])
            ## case where we have a subsample but no labels
            elif labels == None:
                subsampleIndices = self.controller.model.get_subsample_indices(self.subsample)
            ## case where labels are smaller than subsample (usually means model was run on a subsample)
            elif len(labels) < self.subsample:
                self.subsample = len(labels)
                subsampleIndices = self.controller.model.get_subsample_indices(self.subsample)
            ## case where labels and subsample match
            elif len(labels) == self.subsample:
                subsampleIndices = self.controller.model.get_subsample_indices(self.subsample)
            else:
                print "WARNING: something unexpected occured in SaveSubplots subsample handeling"

            ## error check that  labels and subsample match
            if labels == None:
                pass
            elif len(labels) != subsampleIndices.shape[0]:
                print "ERROR: SaveSubplots Error Check -- subsample, labels and events don't match", events.shape, len(labels), type(self.subsample)

            index1,index2 = subplotChannels

            ## labels
            if self.subplotTitles != None:
                if type(self.subplotTitles) == type([]):
                    subplotTitle = self.subplotTitles[subplotIndex]
                elif self.subplotTitles == True:
                    subplotTitle = self.subplotFile
                else:
                    subplotTitle = self.subplotTitles
            else:
                subplotTitle = None
            
            axesLabels = (None,None)
            showNoise = False

            ## handle args
            args = [None for i in range(18)]
            args[0] = self.get_axes(subplotIndex)
            args[1] = events
            args[2] = self.channelList
            args[3] = self.channelDict
            args[4] = index1
            args[5] = index2
            args[6] = subsampleIndices
            args[7] = self.log.log['selected_transform']
            args[8] = labels
            args[9] = subplotHighlight
            args[10] = self.log.log
            args[11] = self.drawState
            args[12] = self.numSubplots
            args[13] = axesLabels
            args[14] = subplotTitle
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
        nga = NoGuiAnalysis(homeDir,channelDict,filePathList,useSubsample=True,makeQaFigs=False,record=False,verbose=False)
        nga.set('subsample_analysis','1000')
        nga.run_model()
    else:
        nga = NoGuiAnalysis(os.path.join(homeDir),channelDict,loadExisting=True)

    figMode = 'analysis'
    numSubplots = 12
    subplotTitles = ["subtitle%s"%i for i in range(numSubplots)]

    ## different ways to test the class
    # exchange nga.controller for homeDir
    # change draw state ['heat','scatter']
    # set the subsample analysis to something different

    ## to test the highlighting
    plotsToViewHighlights = [None for c in range(16)]
    plotsToViewHighlights[1] = [2]
    nga.set('plots_to_view_highlights',plotsToViewHighlights)

    ss = SaveSubplots(nga.controller,figName,numSubplots,figMode=figMode,figTitle='Example title',useScale=True,drawState='scatter',subplotTitles=subplotTitles)
    print 'plot saved as ', figName
