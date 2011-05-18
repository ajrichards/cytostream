#!/usr/bin/python


'''
library for file aligner related functions

'''

import sys,os

from cytostream import NoGuiAnalysis

class FileAlignerII():

    '''
    (1) calculate and save sample statistics
    (2) calculate and save silhouette values
    (3) determine noise
    (4) recalculate silhouette values
    (5) create a template file
    (6) scan all files with template file

    '''


    def __init__(self,expListNames=[],expListData=[],expListLabels=None,phiRange=None,homeDir=None,
                 refFile=None,verbose=False,excludedChannels=[],baseDir=".",
                 modelRunID=None,distanceMetric='mahalanobis'):

        ## declare variables
        self.expListNames = [expName for expName in expListNames]
        self.expListLabels = [[label for label in labelList] for labelList in expListLabels]
        self.phiRange = phiRange
        self.matchResults = None
        self.baseDir = baseDir
        self.homeDir = homeDir
        self.verbose = verbose
        self.isProject = False
        self.modelRunID = modelRunID

        ## control variables 
        self.useMedianShift = True
        self.distanceMetric = distanceMetric
        self.globalScoreDict = {}
        self.newLabelsAll = {}
        self.modelType = 'components'
        
        ## handle exp data
        if type(expListData) != type([]):
            print "ERROR: FileAligner: expListData must be of type list"
            return None
        elif len(expListData) == 0 and self.homeDir == None:
            print "ERROR: without expListData a homDir must be specified"
            return None
        elif len(expListData) == 0 and self.modelRunID == None:
            print "ERROR: without expListData a modelRunID must be specified"
            return None
        elif self.homeDir != None:
            self._init_project()
            self.isProject = True
        else:
            self.expListData = [expData[:,:].copy() for expData in expListData]

        ## handle exluded channels
        events = self.get_events(self.expNamesList[0])
        self.numChannels = np.shape(events)[1]
        if excludedChannels != None:
            self.includedChannels = list(set(range(self.numChannels)).difference(set(excludedChannels)))
        else:
            self.includedChannels = range(self.numChannels)

        ## handle phi range
        if self.phiRange == None:
            phiRange = [0.4,0.8]
        elif type(self.phiRange) != None and type(self.phiRange) != type(np.array([])):
            print "INPUT ERROR: phi range is not a list or np.array"
            return None

    def _init_project(self):
         self.nga = NoGuiAnalysis(homeDir,loadExisting=True)
         self.nga.set("results_mode",self.modelType)
         self.expListNames = self.nga.get_file_names()
         self.fileChannels = self.nga.get_file_channels()

    def get_labels(self,selectedFile):

        if selectedFile not in self.fileList:
            print "ERROR FileAligner _init_labels_events -- bad fileList"
            return
    
        if self.isProject == True:
            statModel, labels = self.nga.get_model_results(selectedFile,self.modelRunID,self.modelType)
            return labels
        else:
            fileInd = self.fileList.index(selectedFile)
            return self.expListLabels[fileInd]

    def get_events(self,selectedFile):

        if selectedFile not in self.fileList:
            print "ERROR FileAligner _init_labels_events -- bad fileList"
            return

        if self.isProject == True:
            modelLog = self.nga.get_model_results_log(selectedFile,self.modelRunID)
            subsample = modelLog['subsample']
            events = nga.get_events(fileName,subsample)
            return events
        else:
            fileInd = self.fileList.index(selectedFile)
            return self.expListData[fileInd]
