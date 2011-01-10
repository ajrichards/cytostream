#!/usr/bin/env python

import sys,os,unittest,time,re
from PyQt4 import QtGui, QtCore
import subprocess

import sys
if sys.platform == 'darwin':
    import matplotlib
    matplotlib.use('Agg')

from cytostream import Controller, get_fcs_file_names
import numpy as np
BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class NoGuiAnalysis():
    def __init__(self,projectID,filePathList,useSubsample=False,makeQaFigs=True,configDict=None):

        ## error checking
        if type(filePathList) != type([]):
            print "INPUT ERROR: filePathList in NoGuiAnalysis input must be of type list"
            return None
        if type(projectID) != type('abc'):
            print "INPUT ERROR: projectID in NoGuiAnalysis input must be of type str"
            return None

        ## declare variables
        self.projectID = projectID
        self.filePathList = filePathList
        self.makeQaFigs = makeQaFigs
        self.configDict = configDict
        self.useSubsample = useSubsample

        ## initialize and load files
        self.initialize()
        self.load_files()

        ## quality assurance figures
        if self.makeQaFigs == True:
            self.make_qa_figures()

        ## run model
        self.run_model()

    def initialize(self):
        """
        initializes a project
        """

        self.controller = Controller(configDict=self.configDict) 
        self.controller.initialize_project(self.projectID)
        self.controller.create_new_project(view=None,projectID=self.projectID)
        
    def load_files(self):
        """
        loads the list of files supplied as input into the project

        """

        self.controller.load_files_handler(self.filePathList)
        self.controller.handle_subsampling(self.controller.log.log['subsample_qa'])
        self.controller.handle_subsampling(self.controller.log.log['subsample_analysis'])

    def get_file_names(self):
        """
        returns all file names associated with a project

        """


        fileList = get_fcs_file_names(self.controller.homeDir)
        
        return fileList

    def update(self):
        """
        update log file status

        """

        self.controller.save()


    def get_events(self,fileName,subsample='original',filterID=None):
        """
        returns the events from a given file name

        """

        fileList = self.get_file_names()
        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping get events"
            return None

        events = self.controller.model.get_events(fileName,subsample=subsample,filterID=filterID)

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


        self.controller.run_selected_model(useSubsample=self.useSubsample)
    
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
