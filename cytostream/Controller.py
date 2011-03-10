#!/usr/bin/env python

'''
The controller class


A.Richards

'''

import re,os,csv,sys,time,re
import subprocess, cPickle
import numpy as np
import Image

try:
    from config_cs import configCS
    pythonPath = configCS['pythonPath']
except:
    pythonPath = 'python'

from PyQt4 import QtGui
from Model import Model
from FileControls import get_fcs_file_names,get_img_file_names,get_models_run,get_project_names
from Logging import Logger

class Controller:
    def __init__(self,viewType=None,configDict=None):
        '''
        construct an instance of the controller class
        to use invoke the method initialize
        '''
        ## get base directory
        if hasattr(sys, 'frozen'):
            self.baseDir = os.path.dirname(sys.executable)
            self.baseDir = re.sub("MacOS","Resources",self.baseDir)
        else:
            self.baseDir = os.path.dirname(__file__)
        
        ## basic application wide variables 
        self.viewType = viewType
        self.appName = "cytostream"
        self.fontName = 'Arial' #'Helvetica'
        self.verbose = False
        self.configDict = configDict
        self.reset_workspace()

    def reset_workspace(self):
        self.projectID = None
        self.homeDir = None

        self.model = Model(verbose=self.verbose)
        self.log = Logger()
        self.subsampleIndices = None
        self.fileChannelPath = None
                              
    def save(self):
        self.log.write()

    def initialize_project(self,projectID,loadExisting=False):
        self.projectID = projectID
        self.homeDir = os.path.join(self.baseDir,"projects",self.projectID)
        self.log.initialize(self.projectID,self.homeDir,load=loadExisting,configDict=self.configDict) 
        self.model.initialize(self.projectID,self.homeDir)

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
        
        for fileName in fileList:
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
                    print 'making img dir', imgDir
                os.mkdir(imgDir)
        
            ## progress point information 
            imageProgress = range(int(numImagesToCreate))
        
            ## specify model type to show as thumbnails
            modelType = self.log.log['thumbnail_results_default']

            ## make the specifed figures
            for indexI,indexJ in comparisons:
                                        
                ## create original for thumbnails
                self.model.create_thumbnail(indexI,indexJ,fileName,subsample,imgDir,modelRunID,modelType)

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
                thumbFile = self.make_thumb(imgFile,thumbDir,fileName)
            
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
            elif len(fileChannels) > 7:
                thumbSize = 70
          
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
        if re.search('filter', str(subsample)):
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
                data = events[self.subsampleIndices,:]
                newDataFileName = fileName + "_data_%s.pickle"%subsample
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
           
    def create_new_project(self,projectID):

        ## create projects dir if necssary
        if os.path.isdir(os.path.join(self.baseDir,'projects')) == False:
            print "INFO: projects dir did not exist. creating..."
            os.mkdir(os.path.join(self.baseDir,'projects'))
        
        ## initialize project
        self.initialize_project(projectID)

        ## remove previous 
        if self.homeDir != None and os.path.exists(self.homeDir) == True:
            if self.verbose == True:
                print 'INFO: overwriting old project of same name...', self.homeDir
            self.remove_project(self.homeDir)

        if self.homeDir != None:
            os.mkdir(self.homeDir)
            os.mkdir(os.path.join(self.homeDir,"data"))
            os.mkdir(os.path.join(self.homeDir,"figs"))
            os.mkdir(os.path.join(self.homeDir,"models"))
            os.mkdir(os.path.join(self.homeDir,"results"))

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

    def load_files_handler(self,fileList,progressBar=None,view=None):
        if type(fileList) != type([]):
            print "INPUT ERROR: load_files_handler: takes as input a list of file paths"
  
        dataType = self.log.log['input_data_type']

        if dataType not in ['fcs','comma','tab']:
            print "INPUT ERROR: load_files_handler: dataType must be of type 'fsc' or 'txt'"

        if dataType in ['comma','tab']:
            if self.fileChannelPath == None:
                allFiles = QtGui.QFileDialog.getOpenFileNames(view,'Load the channels file')
                self.fileChannelPath = str(allFiles[0])

        ## used the selected transform
        transform = self.log.log['selected_transform']
        
        self.model.load_files(fileList,progressBar=progressBar,dataType=dataType,fileChannelPath=self.fileChannelPath)

    def get_component_states(self):
        try:
            return self.view.resultsNavigationLeft.get_component_states()
        except:
            return None

    def handle_filtering(self,fileName,filteringDict):

        subsample = self.log.log['subsample_analysis']
        print 'handling filtering...', subsample

        ## declare variables
        if not re.search('filter', str(subsample)):
            subsample = int(float(subsample))
            
        ## get the filter number id
        subsampleStr = re.sub('filter\d+|\_','',str(subsample))
        if self.log.log['filters_run_count'].has_key(fileName) == False:
            self.log.log['filters_run_count'][fileName] = {subsampleStr:1}
        else:
            if self.log.log['filters_run_count'][fileName].has_key(subsampleStr):
                self.log.log['filters_run_count'][fileName][subsampleStr]+=1
            else:
                self.log.log['filters_run_count'][fileName] = {subsampleStr:1}

        self.save()
       
        filterNumber = int(self.log.log['filters_run_count'][fileName][subsampleStr])
        channels = filteringDict.keys()[0]
        boundries = [int(val) for val in filteringDict.values()[0]]

        print "..............................................................."
        print 'handling filtering...', subsample
        print 'filter number', filterNumber
        print 'filter dict', filteringDict
        print 'filter run count', self.log.log['filters_run_count']
        print "..............................................................."

        filterID = "%s_filter%s"%(subsampleStr,filterNumber)

        ## check to see if a log file has been created for this project
        filterLogFile = os.path.join(self.homeDir,'filterLog.log')
        if os.path.isfile(filterLogFile) == True:
            filterLog = csv.writer(open(filterLogFile,'a'))
        else:
            filterLog = csv.writer(open(filterLogFile,'w'))

        filterLog.writerow([fileName,subsample,filterID,filteringDict]) 

        ## get events
        events = self.model.get_events(fileName,subsample=subsample)

        ## get indices
        xData = events[:,channels[0]]
        yData = events[:,channels[1]]

        xIndices1 = np.where(xData > float(boundries[0]))[0]
        xIndices2 = np.where(xData < float(boundries[1]))[0]
        xIndices = list(set(xIndices1).intersection(set(xIndices2)))

        yIndices1 = np.where(yData > float(boundries[2]))[0]
        yIndices2 = np.where(yData < float(boundries[3]))[0]
        yIndices = list(set(yIndices1).intersection(set(yIndices2)))
        filteredIndices = np.array(list(set(yIndices).intersection(set(xIndices))))
        data = events[filteredIndices,:]
        
        newDataFileName = fileName + "_data_%s.pickle"%filterID
        logFileName = fileName + "_data_%s.log"%filterID
        tmp = open(os.path.join(self.homeDir,'data',newDataFileName),'w')
        cPickle.dump(data,tmp)
        tmp.close()
        logFile = csv.writer(open(os.path.join(self.homeDir,'data',logFileName),'w'))
        logFile.writerow(['filtering dict', str(filteringDict)])
        logFile.writerow(['subsample',subsample])
        logFile.writerow(['original events',str(events.shape[0])])
        logFile.writerow(["timestamp", time.asctime()])

        if os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)) == False:
            print "ERROR: subsampling file was not successfully created", os.path.join(self.homeDir,'data',newDataFileName)

            return True
        else:
            return True

    ##################################################################################################
    #
    # model related
    #
    ##################################################################################################

    def run_selected_model(self,progressBar=None,view=None,useSubsample=True,cleanBorderEvents=True):
        
        ## determine the data in focus
        fileInFocus = self.log.log['file_in_focus']
        numItersMCMC =  int(self.log.log['num_iters_mcmc'])
        selectedModel = self.log.log['model_to_run']
        numComponents = int(self.log.log['dpmm_k'])
        subsample = self.log.log['subsample_analysis']
        fileList = get_fcs_file_names(self.homeDir)
        percentDone = 0
        totalIters = float(len(fileList)) * numItersMCMC
        percentagesReported = []
        self.log.log['models_run_count'] = str(int(self.log.log['models_run_count']) + 1)
        self.save()

        if useSubsample == False:
            subsample = 'original'

        if cleanBorderEvents == True:
            cbe = 't'
        else:
            cbe = 'f'

        ## set the data in focus
        if fileInFocus != 'all' and fileInFocus not in fileList:
            print "ERROR: Controller.run_selected_model -- fileInFocus cannot be found"
        elif fileInFocus != 'all' and fileInFocus in fileList:
            fileList = [fileInFocus]
            
        for fileName in fileList:
            if selectedModel == 'dpmm':
                script = os.path.join(self.baseDir,"RunDPMM.py")
                if os.path.isfile(script) == False:
                    print "ERROR: Invalid model run file path ", script 
                proc = subprocess.Popen("%s %s -h %s -f %s -k %s -s %s -c %s"%(pythonPath,script,self.homeDir,fileName,numComponents,subsample,cbe), 
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
