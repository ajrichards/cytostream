#!/usr/bin/env python

import sys,os,unittest,time,re,cPickle,csv,ast
from PyQt4 import QtGui, QtCore
import subprocess
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from cytostream import Controller, get_fcs_file_names,get_models_run_list
import numpy as np
BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class NoGuiAnalysis():
    def __init__(self,homeDir,channelsDict,filePathList=[],useSubsample=True,makeQaFigs=False,configDict=None,record=True,
                 verbose=False,dType='fcs',inputChannels=None,loadExisting=False,compensationDict=None):
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
        self.compensationDict = compensationDict
        self.channelsDict = channelsDict

        ## initialize
        if loadExisting == False:
            self.initialize()
        else:
            self.initialize_existing()

        ## file channels
        if self.inputChannels != None:
            self.set('alternate_channel_labels',self.inputChannels)

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
        self.controller.create_new_project(self.homeDir,self.channelsDict,record=self.record)
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

        self.controller.compensationDict = self.compensationDict
        self.controller.load_files_handler(self.filePathList,inputChannels=self.inputChannels)
        self.controller.handle_subsampling(self.controller.log.log['subsample_qa'])
        self.controller.handle_subsampling(self.controller.log.log['subsample_analysis'])
        self.controller.handle_subsampling(self.controller.log.log['setting_max_scatter_display'])
        fileChannels = self.controller.model.get_master_channel_list()
        self.set('alternate_channel_labels',fileChannels)
        fileList = self.get_file_names()
        self.set('model_reference', fileList[0])

    def get_file_specific_channels(self,fileName):
        fileChannels = self.controller.model.get_file_channel_list(fileName)
        return fileChannels

    def get_file_channels(self):
        """
        returns file channels
        """

        return self.controller.log.log['alternate_channel_labels']

    def get_file_names(self):
        """
        returns all file names associated with a project

        """

        fileList = get_fcs_file_names(self.controller.homeDir)
        
        return fileList

    def get_models_run(self):
        """
        returns a list of the models run
        
        """

        modelsRun = get_models_run_list(self.controller.log.log)
        
        return modelsRun


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

        events = self.controller.get_events(fileName,subsample=subsample)

        return events

    def get_filter_indices(self,fileName,filterID):
        pickleFile = os.path.join(self.homeDir,'data',fileName + "_indices_%s.pickle"%filterID)
        if os.path.exists(pickleFile) == False:
            print "ERROR: NoGuiAnalysis -- filter indices pickle file does not exist", 
            print "...",pickleFile
            return None

        tmp = open(pickleFile,'r')
        filterIndices = cPickle.load(tmp)
        
        return filterIndices

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

        modelsRun = self.get_models_run()
        if modelRunID not in modelsRun:
            print "ERROR: NoGuiAnalysis -- fileName is not in modelsRun - skipping get model results"
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

    def handle_filtering(self,filterID,fileName,parentModelRunID,modelMode,clusterIDs):
        fileList = self.get_file_names()
        modelsRunList = self.get_models_run()

        ## error checkings
        if type(filterID) != type('abc'):
            print "ERROR: NoGuiAnalysis -- Invalid filter id  - skipping filtering"
            return None
        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping filtering"
            return None
        if parentModelRunID not in modelsRunList:
            print "ERROR: NoGuiAnalysis -- parentModelRun is not in modelsRunList - skipping filtering"
            return None

        self.controller.handle_filtering(filterID,fileName,parentModelRunID,modelMode,clusterIDs,usingIndices)

    def is_valid_filter(self,filterID,fileName):
        '''
        check for a valid filter id
        '''

        filterFile = os.path.join(self.homeDir,'data',fileName + "_indices_%s.pickle"%filterID)
  
        if os.path.exists(filterFile) == False:
            return False
        else:
            return True

    def get_undumped_clusters(self,modelRunID,modelType='components'):

        fileList = self.get_file_names()
        if self.is_valid_filter('dump',fileList[0]) == False:
            print "WARNING: NoGuiAnalysis: cannot access undumped clusters"
            return None

        expListLabels = []
        for fileName in fileList:
            fModel, fClasses = self.get_model_results(fileName,modelRunID,modelType)
            expListLabels.append(fClasses)
        
        ## assemble the undumped clusters                                                                                                                                         
        undumpedClusters = []
        for fileInd in range(len(fileList)):
            fileName = fileList[fileInd]
            fileLabels = expListLabels[fileInd]
            filterIndices = self.get_filter_indices(fileName,'dump')
            undumpedClusters.append(np.unique(fileLabels[filterIndices]).tolist())

        return undumpedClusters

    def handle_filtering_dict(self,fileName,filteringDict):
        fileList = self.get_file_names()

        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping filtering"
            return None

        if type(filteringDict) != type({}):
            print "ERROR: NoGuiAnalysis.handle_filtering -- filteringDict must be of type dict"
    
        self.controller.handle_filtering_dict(fileName,filteringDict)
                                                                                                                                                        
    def get_aligned_labels(self,phi,alignmentDir='alignment'):
        fileName = os.path.join(self.controller.homeDir,alignmentDir,"alignLabels_%s.pickle"%(phi))

        if os.path.exists(fileName) == False:
            print "WARNING: attempted to get aligned labels that do not exist", tmp
            return None

        tmp =  open(fileName,'r')
        alignedLabels = cPickle.load(tmp)
        tmp.close()
        return alignedLabels

    def get_basic_subset_info(self,modelRunID):
        '''        
        get basic subset information
        '''

        bsFilePath = os.path.join(self.controller.homeDir,'results','%s_basic_cell_subsets.csv'%modelRunID)
        if os.path.exists(bsFilePath) == False:
            print "ERROR: NoGuiAnalysis: cannot find basic subsets -- rerun appropriate funciton"
            return None

        reader = csv.reader(open(bsFilePath,'r'))
        header = reader.next()
        fileList = []
        subsetList = []
        totalEventList = []
        percentageList = []
        clusterIDsList = []
        
        for linja in reader:
            fileList.append(linja[0])
            subsetList.append(linja[1])
            totalEventList.append(int(linja[2]))
            percentageList.append(float(linja[3]))
            clusterIDsList.append(ast.literal_eval(linja[4]))
            
        return {'files':fileList,'subsets':subsetList,'totalevents':totalEventList,'percentages':percentageList,'clusters':clusterIDsList}


### Run the tests 
if __name__ == '__main__':
    projectID = 'noguitest'
    allFiles = [os.path.join(BASEDIR,"example_data", "3FITC_4PE_004.fcs")]
    subsample = '1e4'
    nga = NoGuiAnalysis(projectID,allFiles)
