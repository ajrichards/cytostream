#!/usr/bin/env python

import sys,os,unittest,time,re,cPickle,csv,ast
import subprocess
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

from cytostream import Controller, get_fcs_file_names,get_models_run_list
from cytostream.tools import auto_generate_channel_dict
import numpy as np
BASEDIR = os.path.dirname(__file__)

## test class for the main window function
class NoGuiAnalysis():
    """
    Central object for the application programming interface of cytostream.
    """

    def __init__(self,homeDir,filePathList=[],channelDict=None,useSubsample=True,makeQaFigs=False,configDict=None,record=True,
                 verbose=False,dType='fcs',inputChannels=None,loadExisting=False,compensationFilePath=None,transform='logicle',
                 logicleScaleMax=10**5,autoComp=True):
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

        ## ensure basic variables are present
        if loadExisting == False and len(filePathList) == 0:
            print "ERROR: NoGuiAnalysis--filePathList must contain filePaths for a new project"
            return None

        ## attempt to autogenerate the channel dict
        if loadExisting == False and channelDict == None:
            isValidDict,channelDict = auto_generate_channel_dict(filePathList[0])
        else:
            isValidDict = None

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
        self.compensationFilePath = compensationFilePath
        self.autoComp = autoComp
        self.channelDict = channelDict
        self.isValidDict = isValidDict

        ## initialize
        if loadExisting == False:
            self.initialize()
        else:
            self.initialize_existing()

        ## handle channels dict
        if channelDict != None:
            self.controller.model.save_channel_dict(channelDict)
            self.channelDict = self.controller.model.load_channel_dict()
        if channelDict == None:
            self.channelDict = self.controller.model.load_channel_dict()
        else:
            self.channelDict = channelDict
            
        ## file channels
        if self.inputChannels != None:
            self.set('alternate_channel_labels',self.inputChannels)

        ## set the data type
        goFlag = True
        if loadExisting == False:
            print 'NoGuiAnalysis: Initializing %s files of data type %s'%(len(filePathList),dType)
            if dType not in ['fcs','comma','tab','array']:
                print "ERROR in NoGuiAnalysis -- bad input data type", 
                return None
            else:
                self.set('input_data_type',dType)

            ## load files
            self.set('load_transform',str(transform))
            self.set('logicle_scale_max',logicleScaleMax)
            self.set('auto_compensation',self.autoComp)
            goFlag = self.load_files()
            self.set('current_state', 'Model')
            self.set('highest_state', '3')
        else:
            print 'loading existing project'

        ## eusure minimum information present in channel dict 
        fileChannels = self.controller.model.get_master_channel_list()
        self.controller.validate_channel_dict(fileChannels,self.channelDict)
        
        ## quality assurance figures
        if self.makeQaFigs == True:
            if goFlag  == False:
                print "...skipping figure error in file list loading"
            else:
                self.qmake_qa_figures()

    def initialize(self):
        """
        initializes a project
        """

        self.controller = Controller(configDict=self.configDict,debug=self.verbose)
        self.controller.create_new_project(self.homeDir,self.channelDict,record=self.record)

    def initialize_existing(self):
        """
        initialize existing project
        """

        self.controller = Controller(debug=self.verbose)
        self.controller.initialize_project(self.homeDir,loadExisting=True)

    def is_valid(self):
        """
        returns true/false 
        based on whether all channels could be identified in channelDict
        """
        
        if self.isValidDict == None:
            isValidDict = True
            for cname in self.channelDict.iterkeys():
                if cname == 'Unmatched':
                    isValidDict = False

            self.isValidDict = isValidDict

        return self.isValidDict

    def load_files(self):
        """
        loads the list of files supplied as input into the project
        """

        self.controller.compensationFilePath = self.compensationFilePath
        self.controller.load_files_handler(self.filePathList,inputChannels=self.inputChannels)
        self.controller.handle_subsampling(self.controller.log.log['subsample_qa'])
        self.controller.handle_subsampling(self.controller.log.log['subsample_analysis'])
        self.controller.handle_subsampling(self.controller.log.log['setting_max_scatter_display'])
        fileChannels = self.controller.model.get_master_channel_list()
        self.set('alternate_channel_labels',fileChannels)
        fileList = self.get_file_names()
        
        if len(fileList) == 0:
            print "WARNING: No files were loaded"
            return False
        
        self.set('model_reference', fileList[0])

    def load_labels(self,fileName,labelsID,getLog=False):
        """
        returns the labels for a file and a given labelsID
        """
        savedLabels,savedLog = self.controller.get_labels(fileName,labelsID,getLog=True)

        if savedLabels == None:
            #print "WARNING: NoGuiAnalysis -- load_labels returned None. Check your labelsID"
            if getLog == False:
                return None
            else:
                return None,None

        if getLog == True:
            return savedLabels, savedLog
        else:
            return savedLabels

    def save_labels(self,fileName,fileLabels,labelsID):
        """
        saves a set of file labels -- normally generated outside of cytostream
        labels must be vector that is the same size as the number of events in the file
        """

        self.controller.save_labels(fileName,fileLabels,labelsID)

    def save_labels_log(self,fileName,logDict,labelsID):
        """
        saves a log file for file labels
        """

        self.controller.save_labels_log(fileName,logDict,labelsID)

    def get_file_specific_channels(self,fileName):
        fileChannels = self.controller.model.get_file_channel_list(fileName)
        return fileChannels
                 
    def get_file_channels(self):
        """
        returns file channels
        """

        return self.controller.log.log['alternate_channel_labels']

    def get_channel_names(self):
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
            if not re.search('ftr',str(value)):
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
            print "...", fileName
            return None

        events = self.controller.get_events(fileName,subsample=subsample)

        return events

    def make_qa_figures(self,verbose=False):
        """
        makes the figures for quality assurance
        """

        subsample = self.controller.log.log['subsample_qa']
        self.controller.handle_subsampling(subsample)
        self.controller.process_images('qa',verbose=verbose)

    def make_results_figures(self,modelRunID,verbose=False):
        subsample = self.controller.log.log['subsample_analysis']
        self.controller.handle_subsampling(subsample)
        self.controller.process_images('analysis',modelRunID=modelRunID,verbose=verbose)

    def run_model(self):
        """
        runs model for all input files
        """

        subsample = self.controller.log.log['subsample_analysis']
        self.controller.handle_subsampling(subsample)
        self.controller.run_selected_model()

        self.set('current_state', 'Model Results')
        self.set('highest_state', '4')

    def handle_filtering_by_clusters(self,filterID,fileName,clusterIDs,parentModelRunID):
        """
        Filtering saves a np.array using the original array shape where row indices that have
        been filtered become 0 or 1. Filter results can be fetched like labels. 
        """

        fileList = self.get_file_names()
        modelsRunList = self.get_models_run()

        ## error checkings
        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping filtering"
            return None
        if parentModelRunID not in modelsRunList:
            print "ERROR: NoGuiAnalysis -- parentModelRun is not in modelsRunList - skipping filtering"
            return None

        self.controller.handle_filtering_by_clusters(filterID,fileName,parentModelRunID,clusterIDs)

    def handle_filtering_by_indices(self,filterID,fileName,indices,parentModelRun=None):
        """
        Filtering saves a np.array using the original array shape where row indices that have
        been filtered become 0 or 1. Filter results can be fetched like labels. 
        """

        fileList = self.get_file_names()
        modelsRunList = self.get_models_run()

        ## error checkings
        if fileName not in fileList:
            print "ERROR: NoGuiAnalysis -- fileName is not in fileList - skipping filtering"
            return None
        
        self.controller.handle_filtering_by_indices(filterID,fileName,indices,
                                                    parentModelRun=parentModelRun)

    def is_valid_filter(self,filterID,fileName):
        """
        check for a valid filter id
        """

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

    def get_excluded_channels(self, includedChannels):
        '''
        uses official names to return excluded channel names
        '''
        for chan in includedChannels:
            if self.channelDict.has_key(chan) == False:
                print "WARNING: cannot get excluded channels -- channel not present in channelDict"
                return None
        
        includedChannels = list(set(self.channelDict.keys()).difference(includedChannels))
        return includedChannels

    def get_subset_info(self,modelRunID,ssFilePath=None):
        '''        
        get basic subset information
        '''

        if ssFilePath == None:
            ssFilePath = os.path.join(self.controller.homeDir,'results','%s_basic_cell_subsets.csv'%modelRunID)
    
        if os.path.exists(ssFilePath) == False:
            print "ERROR: NoGuiAnalysis: cannot find subset file -- rerun appropriate funciton"
            print "...", ssFilePath
            return None

        reader = csv.reader(open(ssFilePath,'r'))
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
