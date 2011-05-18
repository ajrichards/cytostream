#!/usr/bin/env python

import sys,os,unittest,time,re
from PyQt4 import QtGui, QtCore
import subprocess
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from cytostream import Controller, get_fcs_file_names
import numpy as np
BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class NoGuiAnalysis():
    def __init__(self,homeDir,filePathList=[],useSubsample=True,makeQaFigs=False,configDict=None,record=True,
                 verbose=False,dType='fcs',inputChannels=None,loadExisting=False):
        """
          class constructor 

        """

        ## error checking
        if type(filePathList) != type([]):
            print "INPUT ERROR: filePathList in NoGuiAnalysis input must be of type list"
            return None
        if type(homeDir) != type('abc'):
            print "INPUT ERROR: homedir in NoGuiAnalysis input must be of type str", homeDir
            return None

        ## declare variables
        self.homeDir = homeDir
        self.projectID = os.path.split(self.homeDir)[-1]
        self.filePathList = filePathList
        self.makeQaFigs = makeQaFigs
        self.configDict = configDict
        self.useSubsample = useSubsample
        self.record = record
        self.verbose = verbose
        self.inputChannels = inputChannels

        ## initialize
        if loadExisting == False:
            self.initialize()
        else:
            self.initialize_existing()

        ## set the data type
        if loadExisting == False:
            print 'NoGuiAnalysis: Initializing %s files of data type %s'%(len(filePathList),dType)
            if dType not in ['fcs','comma','tab','array']:
                print "ERROR in NoGuiAnalysis -- bad input data type", 
                return None
            else:
                self.set('input_data_type',dType)

            ## load files
            self.load_files()
            self.set('current_state', 'Model')
            self.set('highest_state', '3')
        else:
            print 'loading existing project'
        

        ## quality assurance figures
        if self.makeQaFigs == True:
            self.make_qa_figures()

    def initialize(self):
        """
        initializes a project
        """

        self.controller = Controller(configDict=self.configDict,debug=self.verbose)
        self.controller.create_new_project(self.homeDir,record=self.record)
    def initialize_existing(self):
        '''
        initialize existing project
        '''
        print 'initializing existing'
        self.controller = Controller(debug=self.verbose)
        self.controller.initialize_project(self.homeDir,loadExisting=True)
  
    def load_files(self):
        """
        loads the list of files supplied as input into the project

        """

        self.controller.load_files_handler(self.filePathList,inputChannels=self.inputChannels)
        self.controller.handle_subsampling(self.controller.log.log['subsample_qa'])
        self.controller.handle_subsampling(self.controller.log.log['subsample_analysis'])
        self.controller.handle_subsampling(self.controller.log.log['setting_max_scatter_display'])
        fileChannels = self.controller.model.get_master_channel_list()
        self.set('alternate_channel_labels',fileChannels)

    def get_file_channels(self):
        """
        returns file channels
        """

        return self.controller.log.log['alternate_file_channels']

    def get_file_names(self):
        """
        returns all file names associated with a project

        """

        fileList = get_fcs_file_names(self.controller.homeDir)
        
        return fileList

    def get(self,key):
        """
        get a value in the log file
        
        """
    
        if self.controller.log.log.has_key(key) == False:
            print "ERROR: in NoGuiAnalysis.get -- invalid key entry",key
            return None
    
        return self.controller.log.log[key]

    def set(self,key,value):
        """
        set a value in the log file
        
        """
        
        if self.controller.log.log.has_key(key) == False:
            print "ERROR: in NoGuiAnalysis.set -- invalid key entry",key
            return None
    
        self.controller.log.log[key] = value
        self.update()
        
        if key == 'subsample_qa' or key == 'subsample_analysis':
            self.controller.handle_subsampling(value)

    def update(self):
        """
        update log file status

        """

        self.controller.save()


    def get_events(self,fileName,subsample='original'):
        """
        returns the events from a given file name

        """

        fileList = self.get_file_names()
        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping get events"
            return None

        events = self.controller.model.get_events(fileName,subsample=subsample)

        return events

    def make_qa_figures(self):
        """
        makes the figures for quality assurance

        """

        subsample = self.controller.log.log['subsample_qa']
        self.controller.handle_subsampling(subsample)
        self.controller.process_images('qa')
    
    def run_model(self):
        """
        runs model for all input files

        """

        subsample = self.controller.log.log['subsample_analysis']
        self.controller.handle_subsampling(subsample)
        self.controller.run_selected_model(useSubsample=self.useSubsample)
        self.set('current_state', 'Results Navigation')
        self.set('highest_state', '4')

    def get_model_results(self,fileName,modelRunID,modelType):
        """
        returns model results

        """
        
        fileList = self.get_file_names()
        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping get model results"
            return None

        statModel, statModelClasses = self.controller.model.load_model_results_pickle(fileName,modelRunID,modelType=modelType)
        
        return statModel, statModelClasses

    def get_model_log(self,fileName,modelRunID):
        """
        returns model run dictionary

        """
        fileList = self.get_file_names()
        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping get model log"
            return None

        modelLog = self.controller.model.load_model_results_log(fileName,modelRunID)
        return modelLog

    def make_results_figures(self,fileName,modelRunID):
        """
        make the results figures for a given file and a given model run

        """

        ## error checking
        modelPath = os.path.join(self.controller.homeDir,'models','%s_%s_classify_components.pickle'%(fileName,modelRunID))
        if os.path.exists(modelPath) == False:
            print "ERROR: model path does not exist did you run the model?"
            return None

        fileList = self.get_file_names()
        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping make results figures"
            return None

        subsample = self.controller.log.log['subsample_analysis']
        self.controller.handle_subsampling(subsample)
        self.controller.process_images('analysis',modelRunID=modelRunID)

    def handle_filtering(self,fileName,filteringDict):
        fileList = self.get_file_names()

        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping filtering"
            return None

        if type(filteringDict) != type({}):
            print "ERROR: NoGuiAnalysis.handle_filtering -- filteringDict must be of type dict"
    
        self.controller.handle_filtering(fileName,filteringDict)

### Run the tests 
if __name__ == '__main__':
    projectID = 'noguitest'
    allFiles = [os.path.join(BASEDIR,"example_data", "3FITC_4PE_004.fcs")]
    subsample = '1e4'
    nga = NoGuiAnalysis(projectID,allFiles)
