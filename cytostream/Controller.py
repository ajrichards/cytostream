#!/usr/bin/env python

'''
The controller class


A.Richards

'''

import re,os,csv,sys,time,re
import subprocess, cPickle
import Image
import numpy as np
import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')

from PyQt4 import QtGui
from Model import Model
from FileControls import get_fcs_file_names,get_img_file_names,get_project_names
from FileControls import add_project_to_log,get_models_run_list
from Logging import Logger
from SaveSubplots import SaveSubplots

try:
    from config_cs import CONFIGCS
except:
    CONFIGCS = {'python_path':'/usr/local/bin/python',
                'number_gpus': 1}

class Controller:
    def __init__(self,viewType=None,configDict=None,debug=False):
        '''
        construct an instance of the controller class
        to use invoke the method initialize
        '''

        ## basic application wide variables 
        self.viewType = viewType
        self.appName = "cytostream"

        ## set debug mode
        self.debug = debug

        if self.debug == True:
            self.verbose = True
        else:
            self.verbose = False

        ## application variables
        self.configDict = configDict
        self.reset_workspace()

    def reset_workspace(self):
        self.projectID = None
        self.homeDir = None
        self.model = Model(verbose=self.verbose)
        self.log = Logger()
        self.subsampleIndices = None
        self.fileChannelPath = None
        self.baseDir = self.model.baseDir
        self.currentPlotView = None
        self.compensationFilePath= None
        self.eventsList = []
        self.fileNameList = None
        self.channelDict = None
        self.subsampleDict = {}

        if self.debug == True:
            print 'DEBUG ON'
            self.verbose = True
            self.defaultDir = os.path.join(self.baseDir,'projects')
        else:
            self.verbose = False
            self.defaultDir = os.getenv("HOME")

        self.pythonPath = self.model.pythonPath                           
        
    def save(self):
        self.log.write()

    def initialize_project(self,homeDir,loadExisting=False):
        self.projectID = os.path.split(homeDir)[-1]
        self.homeDir = homeDir
        self.log.initialize(self.homeDir,load=loadExisting,configDict=self.configDict) 
        self.model.initialize(self.homeDir)
        self.fileNameList = get_fcs_file_names(self.homeDir)

        if len(self.fileNameList) < 25: 
            self.eventsList = [self.model.get_events_from_file(fn) for fn in self.fileNameList]
        else:
            self.eventsList = []

        self.labelsList = {}

        if len(self.fileNameList) > 0:
            self.fileChannels = self.model.get_file_channel_list(self.fileNameList[0])
        else:
            self.fileChannels = None

    def labels_load(self,modelRunID,modelType='components'):
        '''
        load the labels from a given model run
        
        '''

        modelsRunList = get_models_run_list(self.log.log)
        if modelRunID not in modelsRunList:
            print "DEBUGG: no model present"
            return None
        else:
            if self.labelsList.has_key(modelRunID) == True:
                return None
            
            _labelsList = []
            for fileName in self.fileNameList:
                fModel, fClasses = self.model.load_model_results_pickle(fileName,modelRunID,modelType=modelType)
                _labelsList.append(fClasses)
            self.labelsList[modelRunID] = _labelsList
                
    def get_events(self,selectedFileName,subsample='original'):
        '''
            input:
                selectedFileName - string representing the file without the full path and without a file extension
                subsample - any numeric string, int or float that specifies an already processed subsample
                subsample - may also be a filterID such as 'filter1'
        '''
  
        ## error checking
        if selectedFileName not in self.fileNameList:
            print "ERROR: Controller.get_events - Invalid selectedFile specified", selectedFileName
            return None
        
        ## check to see if orig events are in memory otherwise load them from pickle
        if len(self.eventsList) > 0:
            origEvents =  self.eventsList[self.fileNameList.index(selectedFileName)]
        else:
            origEvents =  self.model.get_events_from_file(selectedFileName)

        if subsample == 'original':
            return origEvents
        else:
            self.handle_subsampling(subsample)
            key = str(int(float(subsample)))
            return origEvents[self.subsampleDict[key],:]
    
    def get_labels(self,selectedFileName,modelRunID,modelType='components',subsample='original'):
        modelsRunList = get_models_run_list(self.log.log)

        if modelRunID not in modelsRunList:
            return None

        if selectedFileName not in self.fileNameList:
            print "ERROR: Controller.get_labels - Invalid selectedFile specified", selectedFileName
            return None

        self.labels_load(modelRunID,modelType=modelType)
        labels = self.labelsList[modelRunID][self.fileNameList.index(selectedFileName)]

        if subsample == 'original':
            return labels
        else:
            return labels[self.subsampleDict[key],:]
        
    def process_images(self,mode,modelRunID=None,progressBar=None,view=None):

        ## error check
        if mode not in ['qa','analysis']:
            print "ERROR: invalid mode specified"
            return None

        if mode == 'analysis' and modelRunID == None:
            print "ERROR: controller.process_images - modelRun must be specified"
            return None

        ## declare variables
        numImagesToCreate = 0

        ## ensure alternate_labels have been selected
        if len(self.log.log['alternate_channel_labels']) == 0:
            self.log.log['alternate_channel_labels'] = self.model.get_master_channel_list()
            self.save()

        ## determine mode specific variables
        if mode == 'qa':
            subsample = self.log.log['subsample_qa']
            excludedChannels = self.log.log['excluded_channels_qa']
            excludedFiles = self.log.log['excluded_files_qa']
        elif mode == 'analysis':
            subsample = self.log.log['subsample_analysis']
            excludedChannels = self.log.log['excluded_channels_analysis']
            excludedFiles = self.log.log['excluded_files_analysis']

        if subsample == 'original':
            maxViewSubsample = self.log.log['setting_max_scatter_display']
            self.handle_subsampling(maxViewSubsample)
        
        ## specify which images to create NOTE: assumption that all channel indices are always the same 
        ## this function is still under development and turned OFF by default
        comparisons = self.log.log['thumbnails_to_view']

        if comparisons == None:
            channelIndices = range(len(self.fileChannels))
            comparisons = []
            for i in channelIndices:
                for j in channelIndices:
                    if j >= i or i in excludedChannels or j in excludedChannels:
                        continue
                    comparisons.append((i,j))
            self.log.log['thumbnails_to_view'] = comparisons

        ## get num images to create
        for fileName in self.fileNameList:
            n = float(len(self.fileChannels) - len(excludedChannels))
            numImagesToCreate += (n * (n - 1.0)) / 2.0
        
        percentDone = 0
        imageCount = 0
        
        ## get img dir
        if mode == 'analysis':
            imgDir = os.path.join(self.homeDir,'figs',modelRunID)
        elif mode == 'qa':
            imgDir = os.path.join(self.homeDir,"figs",'qa')

        if os.path.isdir(imgDir) == False:
            if self.verbose == True:
                print 'INFO: making img dir', imgDir
            os.mkdir(imgDir)
        
        for fileInd in range(len(self.fileNameList)):
            fileName = self.fileNameList[fileInd]
         
            ## check to see that file is not in excluded files
            if fileName in excludedFiles:
                continue
    
            ## progress point information 
            imageProgress = range(int(numImagesToCreate))
        
            ## specify model type to show as thumbnails
            modelType = self.log.log['thumbnail_results_default']

            plotsToViewChannels = [(0,1) for i in range(16)]
            plotsToViewFiles = [fileInd for i in range(16)]
            plotsToViewHighlights = [None for i in range(16)]
            plotsToViewRuns = [modelRunID for i in range(16)]
            self.log.log["plots_to_view_files"] = plotsToViewFiles
            self.log.log["plots_to_view_highlights"] = plotsToViewHighlights
            self.log.log["plots_to_view_runs"] = plotsToViewRuns

            for comp in comparisons:
                plotsToViewChannels[0] = comp
                self.log.log["plots_to_view_channels"] = plotsToViewChannels
                self.save()

                figName = os.path.join(imgDir,"%s_%s_%s.%s"%(fileName,
                                                             self.fileChannels[comp[0]],
                                                             self.fileChannels[comp[1]],
                                                             self.log.log['plot_type']))

                script = os.path.join(self.baseDir,"RunMakeScatterPlot.py")
                
                if os.path.isfile(script) == False:
                    print 'ERROR: cannot find RunMakeScatterPlot.py'
                    return False
                else:
                    pltCmd = "%s %s -h %s -f %s -m %s"%(self.pythonPath,script,self.homeDir,figName,mode)

                    proc = subprocess.Popen(pltCmd,shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
                    while True:
                        try:
                            next_line = proc.stdout.readline() 
                            proc.wait()
                            if next_line == '' and proc.poll() != None:
                                break
                            else:
                                print next_line
                        except:
                            proc.wait()
                            break 

                imageCount += 1
                progress = 1.0 / float(len(imageProgress)) *100.0
                percentDone+=progress
                     
                if progressBar != None:
                    progressBar.move_bar(int(round(percentDone)))
                    #print 'moving', percentDone
            
            thumbDir = os.path.join(imgDir,fileName+"_thumbs")
            self.create_thumbs(imgDir,thumbDir,fileName)

    def create_thumbs(self,imgDir,thumbDir,fileName,thumbsClean=True):
        # test to see if thumbs dir needs to be made
        if os.path.isdir(thumbDir) == False:
            os.mkdir(thumbDir)
            
        #if specified clean out the thumbs dir 
        if thumbsClean == True:
            for img in os.listdir(thumbDir):
                os.remove(os.path.join(thumbDir,img))

        # make thumbs anew 
        for img in os.listdir(imgDir):
            if os.path.isfile(os.path.join(imgDir,img)) == True:
                imgFile = os.path.join(imgDir,img)
                self.make_thumb(imgFile,thumbDir,fileName)
                os.remove(imgFile)

    def make_thumb(self,imgFile,thumbDir,fileName):
        if os.path.isfile(imgFile) == True:

            if len(self.fileChannels) <= 4:
                thumbSize = 210
            elif len(self.fileChannels) == 5:
                thumbSize = 160
            elif len(self.fileChannels) == 6:
                thumbSize = 120
            elif len(self.fileChannels) == 7:
                thumbSize = 90
            elif len(self.fileChannels) == 8:
                thumbSize = 70
            elif len(self.fileChannels) == 9:
                thumbSize = 60
            elif len(self.fileChannels) == 10:
                thumbSize = 50
            elif len(self.fileChannels) > 10:
                thumbSize = 40
          
            thumbFile  = os.path.split(imgFile[:-4]+"_thumb.png")[-1]
            thumbFile = os.path.join(thumbDir,thumbFile)

            ## use PIL to create thumb
            size = thumbSize,thumbSize
            im = Image.open(imgFile)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(thumbFile)
        else:
            print "ERROR: bad file name specified",fileName

    def handle_subsampling(self,subsample,isFilter=False):
        '''
        if subsampling is specified at the qa or analysis stage and the number is the same this function enables 
        the use of only a single subsampling.

        When isFilter is set to False -- the subsample arg is an int or float
        When isFilter is set to True  -- the subsample arg is a np.array of indices

        '''

        ## ensure 
        if isFilter == True and type(subsample) != type(np.array([])):
            print "ERROR: Controller.handle_subsampling invalid input with isFilter flag on"
            
        ## if subsample is set to some filter
        if type(subsample) == type('abc') and subsample == 'original':
            return True

        ## handle non filtering subsampling 
        elif subsample != 'original':
            subsample = int(float(subsample))
            
            key = str(int(float(subsample)))
            if self.subsampleDict.has_key(key) == False:
                subsampleIndices = self.model.get_subsample_indices(subsample)
                if type(subsampleIndices) == type(np.array([])):
                    pass
                else:
                    print "WARNING: No subsample indices were returned to controller"
                    return False

                self.subsampleDict[key] = subsampleIndices
            return True
        else:
            return True

    ##################################################################################################
    #
    # data dealings -- handling file, project, model and figure data
    #
    ##################################################################################################

    def create_new_project(self,homeDir,channelDict={},record=True):

        ## initialize project
        self.initialize_project(homeDir)

        ## remove previous
        if os.path.exists(self.homeDir) == True:
            if self.verbose == True:
                print 'INFO: overwriting project of same name...', self.homeDir
            self.remove_project(self.homeDir)

        if self.homeDir != None:
            os.mkdir(self.homeDir)
            os.mkdir(os.path.join(self.homeDir,"data"))
            os.mkdir(os.path.join(self.homeDir,"figs"))
            os.mkdir(os.path.join(self.homeDir,"models"))
            os.mkdir(os.path.join(self.homeDir,"results"))
            os.mkdir(os.path.join(self.homeDir,"documents"))

        ## class wide variables
        self.model.save_channel_dict(channelDict)
        self.fileNameList = get_fcs_file_names(self.homeDir)
        self.channelDict = self.model.load_channel_dict()

        ## record project creation in log
        if record == True:
            add_project_to_log(self.baseDir,self.homeDir,'created')

        ## save progress
        self.save()

        return True

    def remove_project(self,homeDir):        
        for fileOrDir in os.listdir(homeDir):
            if os.path.isfile(os.path.join(homeDir,fileOrDir)) == True:
                os.remove(os.path.join(homeDir,fileOrDir))
            elif os.path.isdir(os.path.join(homeDir,fileOrDir)) == True:
                for fileOrDir2 in os.listdir(os.path.join(homeDir,fileOrDir)):
                    if os.path.isfile(os.path.join(homeDir,fileOrDir,fileOrDir2)) == True:
                        os.remove(os.path.join(homeDir,fileOrDir,fileOrDir2))
                    elif os.path.isdir(os.path.join(homeDir,fileOrDir,fileOrDir2)) == True:
                        for fileOrDir3 in os.listdir(os.path.join(homeDir,fileOrDir,fileOrDir2)):
                            if os.path.isfile(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3)) == True:
                                os.remove(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3))
                            elif os.path.isdir(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3)) == True:     
                                for fileName in os.listdir(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3)):
                                    os.remove(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3,fileName))
                                os.rmdir(os.path.join(homeDir,fileOrDir,fileOrDir2,fileOrDir3))
                        os.rmdir(os.path.join(homeDir,fileOrDir,fileOrDir2))
                os.rmdir(os.path.join(homeDir,fileOrDir))
        os.rmdir(homeDir)

    def rm_fcs_file(self,fcsFile):
        '''
        remove a fcs file from a project

        '''

        dataDir = os.path.join(self.homeDir,'data')
        modelsDir = os.path.join(self.homeDir,'models')
        figsDir = os.path.join(self.homeDir,'figs')
        searchKey1 = fcsFile + "\_data"
        searchKey2 = fcsFile + "\_channels"
        searchKey3 = fcsFile + "\_run"
        searchKey4 = fcsFile + "\_"

        ## remove files from data directory
        for dirFile in os.listdir(dataDir):
            if re.search(searchKey1 + "|" + searchKey2, dirFile):
                os.remove(os.path.join(dataDir,dirFile))

        ## remove files from models directory
        for dirFile in os.listdir(modelsDir):
            if re.search(searchKey3, dirFile):
                os.remove(os.path.join(modelsDir,dirFile))
        
        ## get a list of figures dirs and remove files from each
        figsDirList = []
        for itemName in os.listdir(figsDir):
            if os.path.isdir(os.path.join(figsDir,itemName)):
                figsDirList.append(itemName)

        ## remove all figures
        for dirName in figsDirList:
            for dirFile in os.listdir(os.path.join(figsDir,dirName,fcsFile+"_thumbs")):
                os.remove(os.path.join(figsDir,dirName,fcsFile+"_thumbs",dirFile))
            os.removedirs(os.path.join(figsDir,dirName,fcsFile+"_thumbs"))

            for dirFile in os.listdir(os.path.join(figsDir,dirName)):
                if re.search(searchKey4,dirFile):
                    os.remove(os.path.join(figsDir,dirName,dirFile))

    def load_files_handler(self,fileList,progressBar=None,view=None,inputChannels=None):
        if type(fileList) != type([]):
            print "INPUT ERROR: load_files_handler: takes as input a list of file paths"
  
        dataType = self.log.log['input_data_type']

        if dataType not in ['fcs','comma','tab','array']:
            print "INPUT ERROR: load_files_handler: dataType must be of type 'fsc' 'comma','tab','array'"

        if dataType in ['array'] and inputChannels == None:
            print "ERROR: Controller -- inputChannels must be specified if dType is array"
            return None
        else:
            self.fileChannelPath = inputChannels

        if dataType in ['comma','tab']:
            if self.fileChannelPath == None:
                allFiles = QtGui.QFileDialog.getOpenFileNames(view,'Load the channels file')
                self.fileChannelPath = str(allFiles[0])

        ## used the selected transform
        transform = self.log.log['selected_transform']
        autoComp = self.log.log['auto_compensation']

        self.model.load_files(fileList,progressBar=progressBar,dataType=dataType,fileChannelPath=self.fileChannelPath,
                              compensationFilePath=self.compensationFilePath,transform=transform,autoComp=autoComp)

        ## initialize class wide variables 
        self.fileNameList = get_fcs_file_names(self.homeDir)

        if len(self.fileNameList) < 25:
            self.eventsList = [self.model.get_events_from_file(fn) for fn in self.fileNameList]
        else:
            self.eventsList = []

        self.fileChannels = self.model.get_file_channel_list(self.fileNameList[0])
        self.channelDict = self.model.load_channel_dict()

    def get_component_states(self):
        try:
            return self.view.resultsNavigationLeft.get_component_states()
        except:
            return None

    def get_filter_indices_by_clusters(self,fileName,parentModelRunID,modelMode,clusterIDs):
        '''
        given a set of cluster ids (list) the respective events indices are found and returned

        '''

        if len(clusterIDs) == 0:
            print "WARNING: Controller.get_indices_for_filter -- clusterIDs was empty"
            return False

        #if usingIndices == False:
        statModel, fileLabels = self.model.load_model_results_pickle(fileName,parentModelRunID,modelType=modelMode)
        modelLog = self.model.load_model_results_log(fileName,parentModelRunID)
        #parentFilter = modelLog['filter used']
        #filterID = 'filter%s'%str(int(self.log.log['filters_run_count']) + 1)
        #self.log.log['filters_run_count'] = str(int(self.log.log['filters_run_count']) + 1)
        
        ## check to see if a log file has been created for this project
        #filterLogFile = os.path.join(self.homeDir,"data",'%s.log'%filterID)
        #if os.path.isfile(filterLogFile) == True:
        #    filterLog = csv.writer(open(filterLogFile,'a'))
        #else:
        #    filterLog = csv.writer(open(filterLogFile,'w'))

        ## get events
        #events = self.get_events(fileName,subsample='original')
        
        ## check that labels are of right type
        if type(clusterIDs[0]) != type(1):
            clusterIDs = [int(cid) for cid in clusterIDs]
        if type(clusterIDs) == type([]):
            clusterIDs = np.array(clusterIDs)
            
        ## get indices
        filterIndices = None

        for cid in clusterIDs:
            inds = np.where(fileLabels == cid)[0]

            if filterIndices == None:
                filterIndices = inds
            else:
                filterIndices = np.hstack([filterIndices,inds])
       
        return filterIndices

        #data = events[filterIndices,:]
        #newDataFileName = fileName + "_data_%s.pickle"%filterID
        #filterIndicesFile = fileName + "_indices_%s.pickle"%filterID

        #logFileName = fileName + "_data_%s.log"%filterID
        #tmp1 = open(os.path.join(self.homeDir,'data',newDataFileName),'w')
        #cPickle.dump(data,tmp1)
        #tmp1.close()
        #tmp2 = open(os.path.join(self.homeDir,'data',filterIndicesFile),'w')
        #cPickle.dump(filterIndices,tmp2)
        #tmp2.close()
        #logFile = csv.writer(open(os.path.join(self.homeDir,'data',logFileName),'w'))
        #logFile.writerow(['original events',str(events.shape[0])])
        #logFile.writerow(["timestamp", time.asctime()])

        #if os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)) == False:
        #    print "ERROR: subsampling file was not successfully created", os.path.join(self.homeDir,'data',newDataFileName)
        # 
        #    return False
        #else:
        #    return True

    ##################################################################################################
    #
    # model related
    #
    ##################################################################################################

    def run_selected_model(self,progressBar=None,view=None,useSubsample=True):

        def report_progress(percentComplete,percentReported,progressBar=None):
            if progressBar != None:
                progressBar.move_bar(int(round(percentComplete)))
            else:
                isNew = False
                for _gpu,_percent in percentComplete.iteritems():
                    if int(round(_percent)) not in percentReported[_gpu]:
                        isNew = True
                
                if isNew == True:
                    allComplete = True
                    for _gpu,_percent in percentComplete.iteritems():
                        if int(round(_percent)) != 100:
                            allComplete = False
                    isFirst = True
                    for _gpu,_percent in percentComplete.iteritems():
                        
                        if isFirst == True:
                            print "\r GPU:%s"%_gpu,int(round(_percent)),
                        if isFirst == False:
                            print "GPU:%s"%_gpu,int(round(_percent)),
                        isFirst = False

                    if allComplete == True:
                        print "\nAll models have been run"

        def sanitize_check(script):
            if re.search(">|<|\*|\||^\$|;|#|\@|\&",script):
                return False
            else:
                return True

        ## ensure filelist variable is up to date
        if len(self.fileNameList) == 0:
            self.fileNameList = get_fcs_file_names(self.homeDir)

        ## variables
        numItersMCMC =  int(self.log.log['num_iters_mcmc'])
        selectedModel = self.log.log['model_to_run']
        modelMode = self.log.log['model_mode']
        modelReference = self.log.log['model_reference']
        subsample = self.log.log['subsample_analysis']
        percentDone = 0
        totalIters = float(len(self.fileNameList)) * numItersMCMC
        percentagesReported = []
        fileList = self.fileNameList
        
        modelRunID = 'run%s'%str(int(self.log.log['models_run_count']) + 1)
        self.log.log['models_run_count'] = str(int(self.log.log['models_run_count']) + 1)
        self.save()

        if useSubsample == False:
            subsample = 'original'

        ## error check
        if modelMode == 'onefit':
            print "ERROR: Controller one fit is not a valid model mode"
            sys.exit()

        #if modelMode == 'onefit' and modelReference == None:
        #    print "ERROR: Controller.run_selected_model - cannot use 'onefit' without specifing a model reference"
        #    return

        ## if model mode is 'onefit' ensure the reference file comes first
        if modelMode == 'onefit':
            if fileList.__contains__(modelReference) == False:
                print "ERROR: Controller.run_selected_model - bad model reference"
                return
            
        ## if using model reference ensure ref comes first
        if modelReference != None:    
            refPosition = fileList.index(modelReference)
            if refPosition != 0:
                refFile = fileList.pop(refPosition)
                fileList = [refFile] + fileList

        ## handle GPU identification
        numGPUs = CONFIGCS['number_gpus']

        ## option to force the use of only a single gpu
        if self.log.log['force_single_gpu'] == True:
            numGPUs = 1

        if type(numGPUs) != type(1):
            print "ERROR: Controller numGPUs is invalid variable type"

        ## split the file list among the total number of gpus        
        gpuDeviceList = np.arange(numGPUs)
        fileListByGPU = {}
        
        gpuCount = -1
        for fileInd in range(len(fileList)):
            gpuCount+=1
            if gpuCount > max(gpuDeviceList):
                gpuCount = 0

            if fileListByGPU.has_key(str(gpuCount)) == False:
                fileListByGPU[str(gpuCount)] = []
    
            fileListByGPU[str(gpuCount)].append(fileList[fileInd])

        ## send jobs to appropriate gpu
        for gpu,fList in fileListByGPU.iteritems():
            fListStr = re.sub("\[|\]|\s|\'","",str(fList))
            #fListStr = re.sub(",",";",fListStr)
            script = os.path.join(self.baseDir,"QueueGPU.py")
            if os.path.isfile(script) == False:
                print "ERROR: Invalid model run file path ", script
            
            cmd = "%s %s -b %s -h %s -f %s -g %s"%(self.pythonPath,script,self.baseDir,
                                                   self.homeDir,fListStr,gpu)
            ## sanitize shell input
            isClean = sanitize_check(cmd)
            if isClean == False:
                print "ERROR: An unclean file name or another argument was passed to QueueGPU --- exiting process"
                sys.exit()

            proc = subprocess.Popen(cmd,shell=True)#,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
            
        print "DEBUG: Controller -- all jobs have been sent"


        totalCompletedFiles = 0
        percentComplete = {}
        percentReported = {}
        for gpu in fileListByGPU.keys():
            percentComplete[gpu] = 0.001
            percentReported[gpu] = []

        while totalCompletedFiles < len(self.fileNameList):
            time.sleep(2)
            completedFiles = {}
            for gpu in fileListByGPU.keys():
                completedFiles[gpu] = []

            for fName in os.listdir(os.path.join(self.homeDir,'models')):
                if not re.search("\_%s\.log"%modelRunID,fName):
                    continue
                
                ## count completed files
                actualFileName = re.sub("\_%s\.log"%modelRunID,"",fName)
                for gpu,fList in fileListByGPU.iteritems():
                    if actualFileName in fList:
                        completedFiles[gpu].append(actualFileName)
                        totalCompletedFiles += 1        

                ## print out process
                for gpu,fList in completedFiles.iteritems():
                    _percentComplete = (float(len(completedFiles[gpu])) / float(len(fileListByGPU[gpu]))) * 100.0
                    percentComplete[gpu] = _percentComplete
                    report_progress(percentComplete,percentReported,progressBar=progressBar)

        ## wait until files have been created
        #re1 = re.compile("\_\d\_gpu\.log")
        #re2 = re.compile("\d+")
        #totalCompletedFiles = 0
        #percentComplete = {}
        #percentReported = {}
        #for gpu in fileListByGPU.keys():
        #    percentComplete[gpu] = 0.001
        #    percentReported[gpu] = []
        #
        #report_progress(percentComplete,percentReported,progressBar=progressBar)

        #time.sleep(3)
        #while totalCompletedFiles < len(self.fileNameList):
        #    completedFiles = {}
        #    for gpu in fileListByGPU.keys():
        #        completedFiles[gpu] = []
        #
        #    for fName in os.listdir(os.path.join(self.homeDir,'models')):
        #        if not re.search(re1,fName):
        #            continue
        #        
        #        ## get last line of log file
        #        actualFileName = re.sub(re1,"",fName)
        #        gpuID = re.findall(re1,fName)[0]
        #        gpuID = re.findall(re2,gpuID)[0]
        #
        #        tmp = open(os.path.join(self.homeDir,'models',fName),'rb')
        #        #reader = csv.reader(tmp)
        #        filePercentComplete = None
        #        allLines = tmp.readlines()
        #        if len(allLines) == 0:
        #            tmp.close()
        #            continue
        #        filePercentComplete = float(allLines[-1]) / 100.0
        #        #for linja in reader:
        #        #    if len(linja) == 1:
        #        #        filePercentComplete = float(linja[0]) / 100.0
        #        if filePercentComplete != None:
        #            percentComplete[gpuID] = int((float(filePercentComplete + len(completedFiles[gpuID])) / float(len(fileListByGPU[gpuID]))) * 100.0)
        #            
        #        for gpu,fList in fileListByGPU.iteritems():
        #            if filePercentComplete == 1.0 and actualFileName in fList:
        #                completedFiles[gpu].append(actualFileName)
        #                totalCompletedFiles += 1
        #                break
        #    ## print out process
        #    for gpu,fList in completedFiles.iteritems():
        #        _percentComplete = int(float(len(fList)) / float(len(fileListByGPU[gpu])) * 100.0)
        #        percentComplete[gpu] = _percentComplete
        #        report_progress(percentComplete,percentReported,progressBar=progressBar)

        '''
        fileCount = 0
        for fileName in fileList:
            fileCount += 1
            if selectedModel == 'dpmm':
                script = os.path.join(self.baseDir,"RunDPMM.py")
                if os.path.isfile(script) == False:
                    print "ERROR: Invalid model run file path ", script 
                proc = subprocess.Popen("%s %s -h %s -f %s -k %s -s %s"%(self.pythonPath,script,
                                                                         self.homeDir,fileName,numComponents,subsample), 
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE)
                while True:
                    try:
                        next_line = proc.stdout.readline()
                        if next_line == '' and proc.poll() != None:
                            break
                       
                        ## to debug uncomment the following 2 lines
                        if not re.search("it =",next_line):
                            print next_line
                        
                        if re.search("Error|error|ERROR",next_line) and view != None:
                            view.display_error("There was a problem with your cuda device\n%s"%next_line)

                        if re.search("it =",next_line):
                            progress = 1.0 / totalIters
                            percentDone+=progress * 100.0
                            if progressBar != None:
                                progressBar.move_bar(int(round(percentDone)))
                            else:
                                if int(round(percentDone)) not in percentagesReported:
                                    percentagesReported.append(int(round(percentDone)))
                                    if int(round(percentDone)) != 100: 
                                        print "\r",int(round(percentDone)),"percent complete",
                                    else:
                                        print "\r",int(round(percentDone)),"percent complete"
                    except:
                        break
            
            else:
                print "ERROR: invalid selected model", selectedModel

            ## output progress 
            if modelMode == 'onefit':
                percentDone = float(fileCount) / float(len(fileList)) * 100.0
                
                if progressBar != None:
                    progressBar.move_bar(int(round(percentDone)))
                else:
                    if int(round(percentDone)) != 100: 
                        print "\r",int(round(percentDone)),"percent complete",
                    else:
                        print "\r",int(round(percentDone)),"percent complete"

        '''
