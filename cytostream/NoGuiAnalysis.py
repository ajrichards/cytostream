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
    def __init__(self,projectID,filePathList,makeQaFigs=False,makeResultsFigs=False,configDict=None):

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
        self.makeResultsFigs = makeResultsFigs
        self.configDict = configDict

        ## initialize and load files
        self.initialize()
        self.load_files()

    def initialize(self):
        self.controller = Controller(configDict=self.configDict) 
        self.controller.initialize_project(self.projectID)
        self.controller.create_new_project(view=None,projectID=self.projectID)
        
    def load_files(self):
        self.controller.load_files_handler(self.filePathList)
        self.controller.handle_subsampling(self.controller.log.log['subsample_qa'])
        self.controller.handle_subsampling(self.controller.log.log['subsample_analysis'])

    def get_file_names(self):
        fileList = get_fcs_file_names(self.controller.homeDir)
        
        return fileList

    def get_events(self,fileName,subsample='original'):
        events = self.controller.model.get_events(fileName,subsample=subsample)

        return events
    



    '''
    def initialize(self):
        self.controller = Controller()
        self.controller.initialize_project(self.projectID)
        
        firstFile = True
        goFlag = True
        for fileName in self.allFiles:

            if os.path.isfile(fileName) == False:
                print 'ERROR: Bad file name skipping', fileName
                continue

            print 'adding...', fileName
            fileName = str(fileName)
            if firstFile == True:
                self.controller.create_new_project(fileName)
                firstFile = False
            else:
                goFlag = self.controller.load_additional_fcs_files(fileName)

        if self.controller.homeDir == None:
            print "ERROR: project failed to initialize"
            return
        else:
            print "project created."
        
        # subsampling
        print "handling subsampling"
        self.controller.log.log['subsample'] = self.subsample
        self.controller.handle_subsampling()
        self.controller.save()
        
        # qa image creation
        if self.makeQaFigs == True:
            print 'making qa images'
            self.controller.process_images('qa')

    def run_selected_model(self):
        self.controller.log.log['numComponents'] = self.numComponents
        self.controller.log.log['modelToRun'] = 'dpmm'
        self.controller.run_selected_model()
        selectedFile = self.controller.log.log['selectedFile']
        modelName = "%s_sub%s_dpmm"%(re.sub("\.fcs|\.pickle","",selectedFile),int(float(self.subsample)))
        statModelModes, statModelClasses = self.controller.model.load_model_results_pickle(modelName,'modes')
       
    '''
 
### Run the tests 
if __name__ == '__main__':
    projectID = 'noguitest'
    allFiles = [os.path.join(BASEDIR,"example_data", "3FITC_4PE_004.fcs")]
    subsample = '1e4'
    nga = NoGuiAnalysis(projectID,allFiles)
