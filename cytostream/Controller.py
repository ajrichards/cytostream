'''
The controller class
A.Richards

'''

import csv,sys,time,re,shutil
import numpy as np
from PIL import Image

try:
    from PyQt4 import QtGui, QtCore
except:
    print "IMPORT WARNING: Module PyQt4 is not available"
    sys.exit()

try:
    from config_cs import configCS
    pythonPath = configCS['pythonPath']
except:
    pythonPath = 'python'

import re,os,sys,csv,webbrowser,cPickle
from Model import Model
import subprocess
from FileControls import get_fcs_file_names,get_img_file_names,get_models_run,get_project_names
from Logging import Logger

class Controller:
    def __init__(self,viewType=None):
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
        self.reset_workspace()

    def reset_workspace(self):
        self.projectID = None
        self.homeDir = None
        self.model = Model()
        self.log = Logger()
        self.subsampleIndices = None
                              
    def save(self):
        self.log.write()

    def initialize_project(self,projectID,loadExisting=False):
        self.projectID = projectID
        self.homeDir = os.path.join(self.baseDir,"projects",self.projectID)
        self.log.initialize(self.projectID,self.homeDir,load=loadExisting) 
        self.model.initialize(self.projectID,self.homeDir)

    def process_images(self,mode,progressBar=None,modelName=None,view=None):

        if mode not in ['qa','results']:
            print "ERROR: invalid mode specified"

        modelName = self.log.log['modelToRun']
        fileList = get_fcs_file_names(self.homeDir)
        numImagesToCreate = 0
        
        ## prepare to check for excluded channels and files
        excludedChannels = self.log.log['excludedChannels']
        excludedFiles = self.log.log['excludedFiles']

        if type(self.log.log['excludedFiles']) != type([]):
            excludedFiles = []

        if type(self.log.log['excludedChannels']) != type([]):
            excludedChannels = []
   
        ## recreate file list if there are excluded files
        if excludedFiles > 0:
            for f in excludedFiles:
                fileList.remove(f)
            self.log.log['selectedFile'] == fileList[0]

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

            ## get model name
            if mode == 'results':
                if self.log.log['subsample'] == None or self.log.log['subsample'] == 'All Data':
                    longModelName = re.sub('\.fcs|\.pickle','',fileName)+"_"+modelName
                    imgDir = os.path.join(self.homeDir,'figs',modelName)
                else:
                    longModelName = re.sub('\.fcs|\.pickle','',fileName)+"_sub%s_"%int(float(self.log.log['subsample']))+modelName
                    imgDir = os.path.join(self.homeDir,'figs',"sub%s_"%int(float(self.log.log['subsample']))+modelName)            

                if os.path.isdir(imgDir) == False:
                    if self.verbose == True:
                        print 'making img dir', imgDir
                    os.mkdir(imgDir)
            else:
                imgDir = 'None'
                longModelName = 'None'
        
            ## progress point information 
            imageProgress = range(int(numImagesToCreate))
        
            ## within file comparisions
            fileSpecificIndices = range(len(fileChannels))
        
            ## specify model type to show as thumbnails
            modelType = 'modes'

            ## make all pairwise comparisons
            for i in range(len(fileSpecificIndices)):
                indexI = fileSpecificIndices[i]
                channelI = fileChannels[indexI]
                for j in range(len(fileSpecificIndices)):
                    if j >= i:
                        continue

                    indexJ = fileSpecificIndices[j]
                    channelJ = fileChannels[indexJ]

                    ## check to see that channels are not in excluded channels
                    if channelI in excludedChannels or channelJ in excludedChannels:
                        continue
                    


                    if self.log.log['subsample'] == 'All Data':
                        subset = 'all'
                    else:
                        subset = self.log.log['subsample']
                    
                    script = os.path.join(self.baseDir,"RunMakeFigures.py")
                    if os.path.isfile(script) == False:
                        print 'ERROR: cannot find RunMakeFigures'
                    
                    pltCmd = "%s %s -p %s -i %s -j %s -f %s -s %s -a %s -m %s -t %s -h %s"%(pythonPath,script,self.projectID,indexI,indexJ,fileName,subset,
                                                                                            imgDir,longModelName,modelType,self.homeDir)
                    proc = subprocess.Popen(pltCmd,
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
                                         
                    imageCount += 1
                    progress = 1.0 / float(len(imageProgress)) *100.0
                    percentDone+=progress

                    if progressBar != None:
                        progressBar.move_bar(int(round(percentDone)))
                        #print 'moving', percentDone

            ## create the thumbnails
            if mode == 'qa':
                imgDir = os.path.join(self.homeDir,"figs")
            elif mode == 'results':
                if self.log.log['subsample'] == "All Data":
                    imgDir = os.path.join(self.homeDir,'figs',"%s"%(modelName))
                else:
                    imgDir = os.path.join(self.homeDir,'figs',"sub%s_"%int(float(self.log.log['subsample']))+modelName)

            thumbDir = os.path.join(imgDir,fileName[:-4]+"_thumbs")
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

    def handle_subsampling(self):
        if self.log.log['subsample'] != "original":
            if os.path.isfile(os.path.join(self.homeDir,'data','subsample_%s.pickle'%self.log.log['subsample'])) == False:
                self.model.get_subsample_indices(self.log.log['subsample'])

            tmp = open(os.path.join(homeDir,'data','subsample_%s.pickle'%self.log.log['subsample']),'rb')
            self.subsampleIndices = cPickle.load(tmp)

            if type(self.subsampleIndices) == type(np.array([])):
                pass
            elif self.subsampleIndices == False:
                print "WARNING: No subsample indices were returned to controller"
                return False

            n = len(self.subsampleIndices)

            ## for each file associated with the project
            fileList = get_fcs_file_names(self.homeDir)
            for fileName in fileList:
                ## save a pickled copy of the data object
                data = data[self.subsampleIndices,:]
                outFileName = re.sub("\.pickle|.\fcs|\.txt","",fileName)
                outfile = os.path.join(self.homeDir,'data',"%s_sub%s.pickle"%(outFileName,n))
                tmp = open(outfile,'w')
                cPickle.dump(data,tmp)
            return True
        else:
            return True

    ##################################################################################################
    #
    # data dealings -- handling file, project, model and figure data
    #
    ##################################################################################################
           
    def create_new_project(self,view=None,projectID=None):
        #fcsFileName = str(fcsFileName)
        createNew = True
    
        ## create projects dir if necssary
        if os.path.isdir(os.path.join(self.baseDir,'projects')) == False:
            print "INFO: projects dir did not exist. creating..."
            os.mkdir(os.path.join(self.baseDir,'projects'))

        ## get project id
        if projectID != None:
            pass
        elif createNew == True and projectID == None:
            projectID, ok = QtGui.QInputDialog.getText(view, self.appName, 'Enter the name of your new project:')
            projectID = str(projectID)
            
            if ok == False:
                createNew = False
        else:
            createNew = False
            print "ERROR: creating a new project"

        if createNew == True:
            print 'initializing project...'
            self.initialize_project(projectID)
        else:
            print "WARNING: did not initialize project"
            return False

        # remove previous 
        if self.homeDir != None and os.path.exists(self.homeDir) == True and createNew == True:
            print 'overwriting...', self.homeDir
            self.remove_project(self.homeDir)

        if createNew == True and self.homeDir != None:
            os.mkdir(self.homeDir)
            os.mkdir(os.path.join(self.homeDir,"data"))
            os.mkdir(os.path.join(self.homeDir,"figs"))
            os.mkdir(os.path.join(self.homeDir,"models"))
            os.mkdir(os.path.join(self.homeDir,"results"))

        #    if fcsFileName != None:
        #        self.load_fcs_file(fcsFileName)
        #        self.log.log['selectedFile'] = fcsFileName.split(os.path.sep)[-1]

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

    def rm_fcs_file(self,fcsFileName):
        if os.path.isfile(fcsFileName) == False:
            print "ERROR: could not rm file: %s"%fcsFileName
        else:
            os.remove(fcsFileName)
            self.view.status.set("file removed")

    def load_fcs_files(self,fileList,dataType='fcs',transform='log'):
        if type(fileList) != type([]):
            print "INPUT ERROR: load_fcs_files: takes as input a list of file paths"

        script = os.path.join(self.baseDir,"LoadFile.py")
        self.log.log['transform'] = transform

        for filePath in fileList:
            proc = subprocess.Popen("%s %s -f %s -h %s -d %s -t %s"%(pythonPath,script,filePath,self.homeDir,dataType,transform),
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE)
            while True:
                try:
                    next_line = proc.stdout.readline()
                    if next_line == '' and proc.poll() != None:
                        break

                    ## to debug uncomment the following line     
                    print next_line

                except:
                    break

            ## check to see that files were made
            newFileName = re.sub('\s+','_',os.path.split(filePath)[-1])
            newFileName = re.sub('\.fcs|\.txt|\.out','',newFileName)
            newDataFileName = newFileName +"_data_original.pickle"
            newChanFileName = newFileName +"_channels_original.pickle"
            newFileName = re.sub('\s+','_',filePath[-1])
            if filePath == fileList[0]:
                self.log.log['selectedFile'] = re.sub("\.pickle","",newDataFileName)

            if os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)) == False:
                print "ERROR: data file was not successfully created", os.path.join(self.homeDir,'data',newDataFileName)
            if os.path.isfile(os.path.join(self.homeDir,'data',newChanFileName)) == False:
                print "ERROR: channel file was not successfully created", os.path.join(self.homeDir,'data',newChanFileName)

    #def load_additional_fcs_files(self,fileName=None,view=None):
    #    loadFile = True
    #    fcsFileName = None
    #    if fileName == None:
    #        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open FCS file')
    #
    #    if not re.search('\.fcs',fileName):
    #        fcsFileName = None
    #        view.display_warning("File '%s' was not of type *.fcs"%fileName)
    #    else:
    #        fcsFileName = fileName
    #
    #    if fcsFileName != None:
    #        self.load_fcs_file(fcsFileName)
    #        return True
    #    else:
    #        print "WARNING: bad attempt to load file name"
    #        return False

    def get_component_states(self):
        try:
            return self.view.resultsNavigationLeft.get_component_states()
        except:
            return None

    ##################################################################################################
    #
    # log files
    #
    ##################################################################################################

    def run_selected_model(self,progressBar=None,view=None):
        numItersMCMC = 1100
        selectedModel = self.log.log['modelToRun']
        numComponents = self.log.log['numComponents']
        

        if self.subsampleIndices == None:
            fileList = get_fcs_file_names(self.homeDir)
        elif self.subsampleIndices != None:
            fileList = get_fcs_file_names(self.homeDir,getPickles=True)

        percentDone = 0
        totalIters = float(len(fileList)) * numItersMCMC
        percentagesReported = []
        for fileName in fileList:

            if selectedModel == 'dpmm':
                script = os.path.join(self.baseDir,"RunDPMM.py")
                if os.path.isfile(script) == False:
                    print "ERROR: Invalid model run file path ", script 
                proc = subprocess.Popen("%s %s -h %s -f %s -k %s"%(pythonPath,script,self.homeDir,fileName,numComponents), 
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

                
