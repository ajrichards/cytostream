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
from FileControls import get_fcs_file_names,get_img_file_names,get_models_run,get_project_names
from FileControls import add_project_to_log
from Logging import Logger
from SaveSubplots import SaveSubplots

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
        self.compensationDict = None

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

    def process_images(self,mode,modelRunID=None,progressBar=None,view=None):

        ## error check
        if mode not in ['qa','analysis']:
            print "ERROR: invalid mode specified"
            return None

        if mode == 'analysis' and modelRunID == None:
            print "ERROR: controller.process_images - modelRun must be specified"
            return None

        ## declare variables
        fileList = get_fcs_file_names(self.homeDir)
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
        comparisons = self.log.log['thumbnails_to_view']
        
        if comparisons == None:
            fileChannels = self.model.get_file_channel_list(fileList[0])
            channelIndices = range(len(fileChannels))
            comparisons = []
            for i in channelIndices:
                for j in channelIndices:
                    if j >= i or i in excludedChannels or j in excludedChannels:
                        continue
                    comparisons.append((i,j))
            self.log.log['thumbnails_to_view'] = comparisons

        ## get num images to create
        for fileName in fileList:
            fileChannels = self.model.get_file_channel_list(fileName)
            n = float(len(fileChannels) - len(excludedChannels))
            numImagesToCreate += (n * (n - 1.0)) / 2.0
        
        percentDone = 0
        imageCount = 0
        
        for fileInd in range(len(fileList)):
            fileName = fileList[fileInd]
         
            ## check to see that file is not in excluded files
            if fileName in excludedFiles:
                continue

            ## get img dir
            if mode == 'analysis':
                imgDir = os.path.join(self.homeDir,'figs',modelRunID)
            elif mode == 'qa':
                imgDir = os.path.join(self.homeDir,"figs",'qa')

            if os.path.isdir(imgDir) == False:
                if self.verbose == True:
                    print 'INFO: making img dir', imgDir
                os.mkdir(imgDir)
        
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
            numSubplots = 1
            for comp in comparisons:
                plotsToViewChannels[0] = comp
                self.log.log["plots_to_view_channels"] = plotsToViewChannels
                self.save()

                figName = os.path.join(imgDir,"%s_%s_%s.%s"%(fileName,
                                                             fileChannels[comp[0]],
                                                             fileChannels[comp[1]],
                                                             self.log.log['plot_type']))

                script = os.path.join(self.baseDir,"RunMakeScatterPlot.py")
                ## error checking 
                if os.path.isfile(script) == False:
                    print 'ERROR: cannot find RunMakeScatterPlot.py'
                    return False
                else:
                    pltCmd = "%s %s -h %s"%(self.pythonPath,script,self.homeDir)
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
            fileChannels = self.model.get_file_channel_list(fileName)

            if len(fileChannels) <= 4:
                thumbSize = 210
            elif len(fileChannels) == 5:
                thumbSize = 160
            elif len(fileChannels) == 6:
                thumbSize = 120
            elif len(fileChannels) == 7:
                thumbSize = 90
            elif len(fileChannels) == 8:
                thumbSize = 70
            elif len(fileChannels) == 9:
                thumbSize = 60
            elif len(fileChannels) == 10:
                thumbSize = 50
            elif len(fileChannels) > 10:
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

    def handle_subsampling(self,subsample):
        '''
        if subsampling is specified at the qa or analysis stage and the number is the same this function enables 
        the use of only a single subsampling.

        '''

        ## if subsample is set to some filter
        if str(self.log.log['filter_in_focus']) != "None":
            pass
        elif subsample != 'original':
            subsample = int(float(subsample))
            self.subsampleIndices = self.model.get_subsample_indices(subsample)

            if type(self.subsampleIndices) == type(np.array([])):
                pass
            else:
                print "WARNING: No subsample indices were returned to controller"
                return False

            # save pickle files of subsampled events
            fileList = get_fcs_file_names(self.homeDir)
            for fileName in fileList:
                events = self.model.get_events(fileName,subsample='original')
                n,d = events.shape

                if len(self.subsampleIndices) >= n:
                    data = events
                else:
                    data = events[self.subsampleIndices,:]

                newDataFileName = fileName + "_data_%s.pickle"%subsample

                if os.path.exists(os.path.join(newDataFileName)) == True:
                    return True
                else:
                    tmp = open(os.path.join(self.homeDir,'data',newDataFileName),'w')
                    cPickle.dump(data,tmp)
                    tmp.close()

                    if os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)) == False:
                        print "ERROR: subsampling file was not successfully created", os.path.join(self.homeDir,'data',newDataFileName)

            return True
        else:
            return True

    ##################################################################################################
    #
    # data dealings -- handling file, project, model and figure data
    #
    ##################################################################################################
           
    def create_new_project(self,homeDir,record=True):

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
        
        self.model.load_files(fileList,progressBar=progressBar,dataType=dataType,fileChannelPath=self.fileChannelPath,compensationDict=self.compensationDict)

    def get_component_states(self):
        try:
            return self.view.resultsNavigationLeft.get_component_states()
        except:
            return None

    def handle_filtering(self,filterID,fileName,parentModelRunID,modelMode,clusterIDs):
        '''
        given a set of cluster ids the respective events are saved 

        '''

        statModel, fileLabels = self.model.load_model_results_pickle(fileName,parentModelRunID,modelType=modelMode)
        modelLog = self.model.load_model_results_log(fileName,parentModelRunID)
        parentFilter = modelLog['filter used']
        filterNumber = re.sub("\D","",filterID)
        
        if not re.search('filter', str(parentFilter)):
            parentFilter = None

        ## check to see if a log file has been created for this project
        filterLogFile = os.path.join(self.homeDir,"data",'%s.log'%filterID)
        if os.path.isfile(filterLogFile) == True:
            filterLog = csv.writer(open(filterLogFile,'a'))
        else:
            filterLog = csv.writer(open(filterLogFile,'w'))

        filterLog.writerow([fileName,filterID,str(clusterIDs)]) 

        ## get events
        events = self.model.get_events(fileName,subsample='original',filterID=parentFilter)
        
        ## check that labels are of right type
        if type(clusterIDs[0]) != type(1):
            clusterIDs = [int(cid) for cid in clusterIDs]

        ## get indices
        filterIndices = None

        for cid in clusterIDs:
            inds = np.where(fileLabels == cid)[0]

            if filterIndices == None:
                filterIndices = inds
            else:
                filterIndices = np.hstack([filterIndices,inds])

        data = events[filterIndices,:]
        newDataFileName = fileName + "_data_%s.pickle"%filterID
        logFileName = fileName + "_data_%s.log"%filterID
        tmp = open(os.path.join(self.homeDir,'data',newDataFileName),'w')
        cPickle.dump(data,tmp)
        tmp.close()
        logFile = csv.writer(open(os.path.join(self.homeDir,'data',logFileName),'w'))
        logFile.writerow(['original events',str(events.shape[0])])
        logFile.writerow(["timestamp", time.asctime()])

        if os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)) == False:
            print "ERROR: subsampling file was not successfully created", os.path.join(self.homeDir,'data',newDataFileName)

            return False
        else:
            return True

    ##################################################################################################
    #
    # model related
    #
    ##################################################################################################

    def run_selected_model(self,progressBar=None,view=None,useSubsample=True):
        
        ## determine the data in focus
        fileInFocus = self.log.log['file_in_focus']
        numItersMCMC =  int(self.log.log['num_iters_mcmc'])
        selectedModel = self.log.log['model_to_run']
        numComponents = int(self.log.log['dpmm_k'])
        modelMode = self.log.log['model_mode']
        modelReference = self.log.log['model_reference']
        subsample = self.log.log['subsample_analysis']
        fileList = get_fcs_file_names(self.homeDir)
        percentDone = 0
        totalIters = float(len(fileList)) * numItersMCMC
        percentagesReported = []
        self.log.log['models_run_count'] = str(int(self.log.log['models_run_count']) + 1)
        self.save()

        if useSubsample == False:
            subsample = 'original'

        ## error check
        if modelMode == 'onefit' and modelReference == None:
            print "ERROR: Controller.run_selected_model - cannot use 'onefit' without specifing a model reference"
            return

        ## set the data in focus
        if fileInFocus != 'all' and fileInFocus not in fileList:
            print "ERROR: Controller.run_selected_model -- fileInFocus cannot be found"
        elif fileInFocus != 'all' and fileInFocus in fileList:
            fileList = [fileInFocus]
            
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

        fileCount = 0
        for fileName in fileList:
            fileCount += 1
            if selectedModel == 'dpmm':
                script = os.path.join(self.baseDir,"RunDPMM.py")
                if os.path.isfile(script) == False:
                    print "ERROR: Invalid model run file path ", script 
                proc = subprocess.Popen("%s %s -h %s -f %s -k %s -s %s"%(self.pythonPath,script,self.homeDir,fileName,numComponents,subsample), 
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
