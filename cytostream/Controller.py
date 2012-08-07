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
from FileControls import get_fcs_file_names,get_img_file_names,get_project_names,get_saved_gate_names
from FileControls import add_project_to_log,get_models_run_list
from Logging import Logger
from cytostream.tools import get_official_name_match
from cytostream.tools import get_clusters_from_gate, get_indices_from_gate
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
        self.uniqueLabels = {}

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

        if len(self.fileNameList) < 50: 
            self.eventsList = [self.model.get_events_from_file(fn) for fn in self.fileNameList]
        else:
            print "WARNING: Controller has more than 50 files shoud we be using events list?"
            self.eventsList = [self.model.get_events_from_file(fn) for fn in self.fileNameList]

        self.labelsList = {}
        self.modelsRunLog = {}

        if len(self.fileNameList) > 0:
            self.fileChannels = self.model.get_file_channel_list(self.fileNameList[0])
        else:
            self.fileChannels = None

        if self.channelDict == None:
            self.channelDict = self.model.load_channel_dict()

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
            _logsList = []
            for fileName in self.fileNameList:
                fModel, fClasses = self.model.load_model_results_pickle(fileName,modelRunID,modelType=modelType)
                modelLog = self.model.load_model_results_log(fileName,modelRunID)
                _labelsList.append(fClasses)
                _logsList.append(modelLog)
            self.labelsList[modelRunID] = _labelsList
            self.modelsRunLog[modelRunID] = _logsList

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
    
    def get_labels(self,selectedFileName,modelRunID,modelType='components',subsample='original',getLog=False):
        """
        returns labels for a given file and run id
        """
        
        if modelType != 'components':
            print "WARNING: Controller -- cytostream defaults to the use of components"
            modelType = 'components'

        modelsRunList = get_models_run_list(self.log.log)

        if modelRunID not in modelsRunList:
            return None
        if selectedFileName not in self.fileNameList:
            print "ERROR: Controller.get_labels - Invalid selectedFile specified", selectedFileName
            return None

        ## ensure labels are present
        self.labels_load(modelRunID,modelType=modelType)
        labels = self.labelsList[modelRunID][self.fileNameList.index(selectedFileName)]
        modelRunLog = self.modelsRunLog[modelRunID][self.fileNameList.index(selectedFileName)]

        if subsample == 'original':
            labelsToReturn = labels
        else:
            labelsToReturn = labels[self.subsampleDict[key],:]
        
        if getLog == True:
            return modelRunLog,labelsToReturn
        else:
            return labelsToReturn

    def process_images(self,mode,modelRunID=None,progressBar=None,view=None,verbose=False):

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
        
        ## use the variable 'default_thumb_channels' to set thumbnails to view
        if self.channelDict == None or len(self.channelDict) == 0:
            self.channelDict = self.model.load_channel_dict()

        channelThumbs = []
        channelIndices = []
        channelMap = []
        defaultThumbChannels = self.log.log['default_thumb_channels']
        for channel in defaultThumbChannels:
            if channel == 'FSC':
                for channel in ['FSCA','FSCH','FSCW','FSC']:
                    if self.channelDict.has_key(channel):
                        channelIndices.append(self.channelDict[channel])
                        channelThumbs.append(channel)
                        break
            elif channel == 'SSC':
                for channel in ['SSCA','SSCH','SSCW','SSC']:
                    if self.channelDict.has_key(channel):
                        channelIndices.append(self.channelDict[channel])
                        channelThumbs.append(channel)
                        break
            else:
                if self.channelDict.has_key(channel):
                    channelIndices.append(self.channelDict[channel])
                    channelThumbs.append(channel)

        maxNumComparisons = 5
        if len(channelIndices) < 3:
            channelIndices = range(len(self.fileChannels))[:maxNumComparisons]
            channelThumbs = [get_official_name_match(i) for i in self.fileChannels[:maxNumComparisons]]
            self.log.log['default_thumb_channels'] = channelThumbs
            self.save()

        comparisons = []
        for _j,chanj in enumerate(channelThumbs):
            j = self.channelDict[chanj]
            for _i,chani in enumerate(channelThumbs):
                if _j == _i:
                    continue
                i = self.channelDict[chani]
                comparisons.append((i,j))
        self.log.log['thumbnails_to_view'] = comparisons

        ## get channels to be viewed
        channelInds = set([])
        for comp in comparisons:
            channelInds.update(comp)

        ## save the thumb channel map
        self.log.log['default_thumb_channels'] = channelThumbs
        self.save()

        ## get num images to create
        for fileName in self.fileNameList:
            numImagesToCreate += len(comparisons)
 
        percentDone = 0
        imageCount = 0
        
        ## get img dir
        if mode == 'analysis':
            imgDir = os.path.join(self.homeDir,'figs',modelRunID)
            subsample=self.log.log['subsample_analysis']
        elif mode == 'qa':
            imgDir = os.path.join(self.homeDir,"figs",'qa')
            subsample=self.log.log['subsample_qa']

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
            imageProgress = range(int(numImagesToCreate)+(len(channelThumbs)*len(self.fileNameList)))
        
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

                figName = os.path.join(imgDir,"%s_%s_%s.%s"%(fileName,comp[0],comp[1],self.log.log['plot_type']))
                script = os.path.join(self.baseDir,"RunMakeScatterPlot.py")
                
                if os.path.isfile(script) == False:
                    print 'ERROR: cannot find RunMakeScatterPlot.py'
                    return False
                else:
                    pltCmd = "'%s' '%s' -h '%s' -f '%s' -m '%s' -s '%s'"%(self.pythonPath,script,self.homeDir,figName,mode,subsample)
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
            
                if verbose == True:
                    print percentDone

            for chan in channelThumbs:
                chanInd = self.channelDict[chan]
                figName = os.path.join(imgDir,"%s_%s.%s"%(fileName,chan,self.log.log['plot_type']))
                script = os.path.join(self.baseDir,"RunMakeHistogramPlot.py")

                if os.path.isfile(script) == False:
                    print 'ERROR: cannot find RunMakeHistogramPlot.py'
                    return False
                else:
                    pltCmd = "'%s' '%s' -h '%s' -f '%s' -c '%s' -s '%s'"%(self.pythonPath,script,self.homeDir,figName,chanInd,subsample)
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

                if verbose == True:
                    print percentDone
                     
                if progressBar != None:
                    progressBar.move_bar(int(round(percentDone)))
            
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

        comparisons = self.log.log['thumbnails_to_view']

        channels = self.fileChannels
        if os.path.isfile(imgFile) == True:

            if len(comparisons) <= 4:
                thumbSize = 250
            elif len(comparisons) <= 8:
                thumbSize = 200
            elif len(comparisons) <= 12:
                thumbSize = 180
            elif len(comparisons) <= 16:
                thumbSize = 160
            elif len(comparisons) <= 20:
                thumbSize = 140
            elif len(comparisons) <= 24:
                thumbSize = 120
            elif len(comparisons) <= 28:
                thumbSize = 100
            else:
                thumbSize = 50
          
            thumbFile  = os.path.split(imgFile[:-4]+"_thumb.png")[-1]
            thumbFile = os.path.join(thumbDir,thumbFile)

            ## use PIL to create thumb
            size = thumbSize,thumbSize
            im = Image.open(imgFile)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(thumbFile)
        else:
            print "ERROR: bad file name specified",fileName

    def get_subsample_indices(self,subsample):
        if subsample == 'original':
            return

        self.handle_subsampling(subsample)
        key = str(int(float(subsample)))
        return self.subsampleDict[key]

    def handle_subsampling(self,subsample,isFilter=False):
        '''
        handels subsampling by fetching saved indices
        if subsampling is specified at the qa or analysis stage and the number is the same 
        this function enables the use of only a single subsampling.

        When isFilter is set to False -- the subsample arg is an int or float
        When isFilter is set to True  -- the subsample arg is a np.array of indices

        '''

        ## ensure
        if isFilter == True and type(subsample) != type(np.array([])):
            print "ERROR: Controller.handle_subsampling invalid input with isFilter flag on"
            
        ## if subsample is set to some filter
        if subsample == 'original':
            return True
        if re.search('ftr',str(subsample)):
            return True

        ## handle non filtering subsampling
        elif subsample != 'original':
            subsample = int(float(subsample))
            
            key = str(subsample)
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

    def create_new_project(self,homeDir,channelDict={},record=True):
        """
        create a new project
        """

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
        """
        remove a fcs file from a project
        """

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
                defaultDir = os.path.join(self.homeDir,os.path.pardir)
                allFiles = QtGui.QFileDialog.getOpenFileNames(view,'Load the channels file',directory=defaultDir)
                self.fileChannelPath = str(allFiles[0])

        ## used the selected transform
        transform = self.log.log['load_transform']
        autoComp = self.log.log['auto_compensation']
        logicleScaleMax = self.log.log['logicle_scale_max']

        self.model.load_files(fileList,progressBar=progressBar,dataType=dataType,fileChannelPath=self.fileChannelPath,
                              compensationFilePath=self.compensationFilePath,transform=transform,autoComp=autoComp,
                              logicleScaleMax=logicleScaleMax)

        ## reload the log file and save it      
        self.log = Logger()
        self.log.initialize(self.homeDir,load=True)
        self.save()

        ## initialize class wide variables 
        self.fileNameList = get_fcs_file_names(self.homeDir)

        if len(self.fileNameList) < 50:
            self.eventsList = [self.model.get_events_from_file(fn) for fn in self.fileNameList]
        else:
            self.eventsList = []

        if len(self.fileNameList) > 0:
            self.fileChannels = self.model.get_file_channel_list(self.fileNameList[0])
        self.channelDict = self.model.load_channel_dict()

    def handle_filtering_by_clusters(self,filterID,fileName,parentModelRunID,modelMode,clusterIDs):
        modelsRunList = get_models_run_list(self.log.log)

        ## error checkings 
        if fileName not in self.fileNameList:
            print "ERROR: Controller.handle_filtering_by_clusters -- fileName is not in fileList - skipping filtering"
            return None
        if parentModelRunID not in modelsRunList:
            print "ERROR: Controller.handle_filtering_by_clusters -- parentModelRun is not in modelsRunList - skipping filtering"
            return None

        filterIndices = self.model.get_filter_indices_by_clusters(fileName,parentModelRunID,modelMode,clusterIDs)
        self.model.save_filter_indices(fileName,parentModelRunID,modelMode,filterIndices,filterID)

    def handle_filtering_by_indices(self,filterID,fileName,parentModelRunID,modelMode,filterIndices):
        modelsRunList = get_models_run_list(self.log.log)

        ## error checkings 
        if fileName not in self.fileNameList:
            print "ERROR: Controller.handle_filtering_by_clusters -- fileName is not in fileList - skipping filtering"
            return None

        self.model.save_filter_indices(fileName,parentModelRunID,modelMode,filterIndices,filterID)

    def validate_channel_dict(self,fileChannels,channelDict):
        """
        ensure a valid channel dict
        """

        if fileChannels == None or len(fileChannels) == 0:
            print "WARNING: Controller.validate_channel_dict invalid file channels specified"
            print '...', fileChannels
            return False

        mismatchFound = False
        for key,chanInd in channelDict.iteritems():
            keyParts = key.split("+")
            for k in keyParts:
                if k == 'ifng':
                    k = 'ifng|ifn'
                if k == 'dump':
                    k = "dump|cd14|cd19|vamine"

            if chanInd >= len(fileChannels):
                print "WARNING: Controller.validate_channel_dict -- chan indx is invalid %s is larger than %s"%(chanInd,len(fileChannels))
                return False

            strippedChannelName = re.sub("\s|\-|\_","",fileChannels[chanInd])
            if not re.search(k,strippedChannelName,flags=re.IGNORECASE):
                print "WARNING: Controller.validate_channel_dict file channel to channel dict mismatch?", key, fileChannels[chanInd]
                mismatchFound = True

        if mismatchFound == True:
            return False
        else:
            return True

    def sanitize_check(self,script):
        """
        standard function to sanitize file name inputs
        """

        if re.search(">|<|\*|\||^\$|;|#|\@|\&",script):
            return False
        else:
            return True

    def run_selected_model_gpu(self,progressBar=None,view=None):
        """
        used for gpu enabled models
        """

        def report_progress(percentComplete,percentReported,progressBar=None):
            if progressBar != None:
                #progressBar.move_bar(int(round(percentComplete)))
                totalProgress = 0
                for _gpu,_percent in percentComplete.iteritems():
                    totalProgress += float(_percent)
                
                pComplete = totalProgress / (len(percentComplete) * 100.0)
                progressBar.move_bar(int(round(pComplete)))

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
                            print "\rGPU:%s"%_gpu,int(round(_percent)),
                        if isFirst == False:
                            print "GPU:%s"%_gpu,int(round(_percent)),
                        isFirst = False

                    if allComplete == True:
                        print "\nAll models have been run"

        ## ensure filelist variable is up to date
        if len(self.fileNameList) == 0:
            self.fileNameList = get_fcs_file_names(self.homeDir)

        ## variables
        percentDone = 0
        percentagesReported = []
        fileList = self.fileNameList
        
        ## iterate models run
        self.log.log['models_run_count'] = str(int(self.log.log['models_run_count']) + 1)
        modelRunID = 'run'+self.log.log['models_run_count']
        self.log.log['selected_model'] = modelRunID
        self.save()

        ## if model mode is 'onefit' ensure the reference file comes first
        modelMode = self.log.log['model_mode']
        modelReference = self.log.log['model_reference']
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
        selectedModel = self.log.log['model_to_run']
        gpuDeviceList = np.arange(numGPUs)
        fileListByGPU = {}
        
        print 'running... %s via %s'%(selectedModel,self.model.modelsInfo[selectedModel][1])
        print '\tusing %s gpu devices'%len(gpuDeviceList)

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
            script = os.path.join(self.baseDir,"QueueGPU.py")
            if os.path.isfile(script) == False:
                print "ERROR: Invalid model run file path ", script
            
            cmd = "'%s' '%s' -b '%s' -h '%s' -f '%s' -g '%s' -s '%s'"%(self.pythonPath,script,self.baseDir,
                                                                       self.homeDir,fListStr,gpu,
                                                                       selectedModel)
            ## sanitize shell input
            isClean = self.sanitize_check(cmd)
            if isClean == False:
                print "ERROR: An unclean file name or another argument was passed to QueueGPU --- exiting process"
                sys.exit()

            proc = subprocess.Popen(cmd,shell=True)
            
        if self.verbose == True:
            print "INFO: Controller -- all jobs have been sent"

        totalCompletedFiles = 0
        percentComplete = {}
        percentReported = {}
        for gpu in fileListByGPU.keys():
            percentComplete[gpu] = 0.001
            percentReported[gpu] = []

        ## update progress bar or prompt out by tracking log files
        while totalCompletedFiles < len(self.fileNameList):
            time.sleep(3)
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

    def run_selected_model_cpu(self,progressBar=None,view=None):

        def report_progress(percentComplete,percentagesReported,progressBar=None):
            if progressBar != None:
                progressBar.move_bar(int(round(percentComplete)))
            else:
                if int(round(percentComplete)) in percentagesReported:
                    return
                
                percentagesReported.append(int(round(percentComplete)))
                if int(round(percentComplete)) != 100: 
                    print "\r",int(round(percentComplete)),"percent complete",
                else:
                    print "\r",int(round(percentComplete)),"percent complete"
                
        ## ensure filelist variable is up to date
        if len(self.fileNameList) == 0:
            self.fileNameList = get_fcs_file_names(self.homeDir)

        ## variables
        selectedModel = self.log.log['model_to_run']
        percentComplete = 0
        percentagesReported = []
        fileList = self.fileNameList
        
        ## iterate the model run ID
        self.log.log['models_run_count'] = str(int(self.log.log['models_run_count']) + 1)
        modelRunID = 'run'+self.log.log['models_run_count']
        self.log.log['selected_model'] = modelRunID
        self.save()

        if selectedModel not in self.model.modelsInfo.keys():
            print "ERROR: Controller.run_selected_model_cpu -- Invalid model",selectedModel
            return
        
        print 'running... %s via %s'%(selectedModel,self.model.modelsInfo[selectedModel][1])

        cmd = self.pythonPath
        script = os.path.join(self.baseDir,self.model.modelsInfo[selectedModel][1])

        if view == None:
            fileCount = 0
            for fileName in fileList:
                fileCount += 1
                if os.path.isfile(script) == False:
                    print "ERROR: Invalid model run file path ", script
            
                argsStr = "'%s' -h '%s' -f '%s'"%(script,self.homeDir,fileName)
                proc = subprocess.Popen(cmd + ' ' + argsStr, 
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE)
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
        else:
             view.mc.init_model_process(cmd,script,fileList)

    def save_gate(self,gateName,verts,channel1,channel2,channel1Name,channel2Name,parent,fileName,
                  modelRunID='run1',modelMode='components'):
        '''
        saves a given gate
        channels are the channel index

        iFilter - is a filter created using indices within a gate
        cFilter - is a filter created using indices derived from clusters within a gate
        '''
        
        isCytokine = False
        cytokineChan = None
        parent = re.sub("\s+","_",parent)
        gateName = re.sub("\s+","_",gateName)
        parent = re.sub("\.gate","",parent)
        gateName = re.sub("\.gate","",gateName)
        gateFilePath = os.path.join(os.path.join(self.homeDir,"data"),gateName)

        pattern = re.compile("IFN|IFNG|CD27|CD45|CD107|IL2",re.IGNORECASE)
        if re.search(pattern,gateName):
            isCytokine = True
            if re.search(pattern,channel1Name):
                cytokineChan = 0
            if re.search(pattern,channel2Name):
                cytokineChan = 1
            
            ## rewrite the verts to be a stright line
            #cytoThreshold = np.array([i[cytokineChan] for i in verts]).min()
            #if cytokineChan == 1:
            #    verts = [(i[0],cytoThreshold) for i in verts]
            #elif cytokineChan == 0:
            #    verts = [(cytoThreshold,i[1]) for i in verts]

        gateToSave = {'verts':verts,
                      'channel1':channel1,
                      'channel2':channel2,
                      'parent':parent,
                      'name':gateName,
                      'cytokine':isCytokine}

        if not re.search("\.gate",gateFilePath):
            gateFilePath = gateFilePath+".gate"

        tmp1 = open(gateFilePath,'w')
        cPickle.dump(gateToSave,tmp1)
        tmp1.close()

        ## create filters for each file using both indices and clusters
        #for fileName in self.fileNameList:
        fileEvents = self.get_events(fileName)
        fileLabels = self.get_labels(fileName,modelRunID)
        _gateClusters = get_clusters_from_gate(fileEvents[:,[channel1,channel2]],fileLabels,verts)
        _gateClusters = [str(int(c)) for c in _gateClusters]
        _gateIndices  = get_indices_from_gate(fileEvents[:,[channel1,channel2]],verts)

        if parent != 'root':
            parentGate = self.load_gate(parent)
            parentClusterIndices = self.model.load_filter(fileName,'cFilter_%s'%parent)
            if str(parentClusterIndices) == 'None':
                parentClusters = []
            else:
                parentClusters = np.unique(fileLabels[parentClusterIndices])
            parentClusters = [str(int(c)) for c in parentClusters]
            parentIndices = self.model.load_filter(fileName,'iFilter_%s'%parent)
            gateClusters = list(set(parentClusters).intersection(set(_gateClusters)))
            gateIndices = list(set(parentIndices).intersection(set(_gateIndices)))
        else:
            gateClusters = _gateClusters
            gateIndices = _gateIndices

        ## only save cytokine filters for events by index
        if isCytokine == False:
            self.handle_filtering_by_clusters('cFilter_%s'%gateName,fileName,modelRunID,modelMode,gateClusters)
            self.handle_filtering_by_indices('iFilter_%s'%gateName,fileName,modelRunID,modelMode,gateIndices)
        else:
            self.handle_filtering_by_indices('iFilter_%s'%gateName,fileName,modelRunID,modelMode,gateIndices)

    def load_gate(self,gateID):
        '''
        loads the gate from a pickle file
        '''

        gateList = get_saved_gate_names(self.homeDir)
        if gateID not in gateList:
            print "ERROR: Controller.load_gate -- invalid gate specified",gateID
            return
        
        gateFilePath = os.path.join(self.homeDir,'data','%s.gate'%gateID)
        tmp = open(gateFilePath,'r')
        gate = cPickle.load(tmp)
        tmp.close()

        return gate

    def save_subplots(self,figName,numSubplots,figMode='analysis',figTitle=None,useScale=False,drawState='heat',
                      subplotTitles=None,gatesToShow=None,positiveToShow=None,drawLabels=True,textToShow=None):
        '''
        function used from within cytostream when SaveSubplots cannot be imported
        '''

        ss = SaveSubplots(self,figName,numSubplots,figMode=figMode,figTitle=figTitle,useScale=useScale,drawLabels=drawLabels,
                          drawState=drawState,subplotTitles=subplotTitles,gatesToShow=gatesToShow,positiveToShow=positiveToShow,
                          textToShow=textToShow)
