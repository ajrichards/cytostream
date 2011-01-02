#!/usr/bin/env python
"""
The Model class is a interactive layer between cytostream, fcm and outside packages like fcm.
It also handles reusable data manipulation functions, project initialization and other functions.
The class can be used alone for example to interface with fcm.

> import numpy as np
> from cytostream import Model
> projectID = 'utest'
> homeDir = os.path.join("..","cytostream","projects",projectID)
> model = Model()
> model.initialize(projectID, homeDir)
> fcsPathName = os.path.join("..","cytostream","example_data", "3FITC_4PE_004.fcs")
> fcsFileName ="3FITC_4PE_004.fcs"
> data = model.pyfcm_load_fcs_file(fcsFileName)
> events,channels = np.shape(data)
> fileChannelList = model.get_file_channel_list(fcsFileName)
> allChannels = model.get_master_channel_list()

Adam Richards
adam.richards@stat.duke.edu
"""

import sys,csv,os,re,cPickle,subprocess
sys.path.append("/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages")
import numpy as np
from FileControls import get_fcs_file_names,get_img_file_names,get_models_run,get_project_names
from matplotlib import rc
import matplotlib.cm as cm
rc('font',family = 'sans-serif')

class Model:
    """ 
    Class to carry out interfacing with data files and fcm library
    class is first created then initialized
        
    syntax:
        model = Model()
        model.initialize(projectID, homeDir)
    """

    def __init__(self):
        """
        about:
            Basic constructor method.  Class must be initialized before use. 
        input:
            None
        return:
            None
        """
        self.projectID = None
        self.homeDir = None

    def initialize(self,projectID,homeDir):
        """
        about:
            Associates a class with a project and home directory. The function
            also sets the python path.
        input:
            projectID - a string for the project name
            homeDir - is the full path for the home dir including the projectID
        return:
            None
        """
        ## initialize project
        self.projectID = projectID
        self.homeDir = homeDir
        
        ## get base directory 
        if hasattr(sys, 'frozen'):
            self.baseDir = os.path.dirname(sys.executable)
            self.baseDir = re.sub("MacOS","Resources",self.baseDir)
        else:
            self.baseDir = os.path.dirname(__file__)

        ## set python path
        self.pythonPath = os.path.join(os.path.sep,"usr","bin","python")

    def load_files(self,fileList,dataType='fcs',transform='log'):
        """
        about: 
            This is a handler function for the script LoadFile.py which loads an fcs
            or txt file of flow cytometry data.  For the binary fcs normally this is 
            carried out using the fcm python module.  This method is called by
            controlller.load_files_handler.
        input:
            fileList - a list of full paths to fcs or txt files
            dataType - may be any of the following: fcs,txt
            transform - may be any of the follwing: log 
        return:
            None
        """

        ## error checking
        if type(fileList) != type([]):
            print "INPUT ERROR: load_files: takes as input a list of file paths"
            return None
        if os.path.isdir(self.homeDir) == False:
            os.mkdir(self.homeDir)
            os.mkdir(os.path.join(self.homeDir,"data"))
            print "INFO: making home dir from Model"

        ## get python path
        script = os.path.join(self.homeDir,"..","..","LoadFile.py")
        for filePath in fileList:
            proc = subprocess.Popen("%s %s -f %s -h %s -d %s -t %s"%(self.pythonPath,script,filePath,self.homeDir,dataType,transform),
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

            if os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)) == False:
                print "ERROR: data file was not successfully created", os.path.join(self.homeDir,'data',newDataFileName)
            if os.path.isfile(os.path.join(self.homeDir,'data',newChanFileName)) == False:
                print "ERROR: channel file was not successfully created", os.path.join(self.homeDir,'data',newChanFileName)

    def get_events(self,fileName,subsample='original'):
        """
        about:
            this function handles the fetching of the events associated with a given file.
            those events may be either all (original) or some specified subset.  To succesfully obtain a 
            subsample the function model.get_subsample_indices must first be run.
        input:
            fileName - string representing the file without the full path and without a file extension
            subsample - any numeric string, int or float that specifies an already processed subsample 
        return:
            a np.array of event data
        """
        
        if subsample != 'original':
            subsample = str(int(float(subsample)))

        fileName = fileName + "_data_" + subsample + ".pickle"
        if os.path.isfile(os.path.join(self.homeDir,'data',fileName)) == False:
            print "INPUT ERROR: bad file name specified in model.get_events"
            print "\t", os.path.join(self.homeDir,'data',fileName)
            return None
        
        tmp = open(os.path.join(self.homeDir,'data',fileName),'rb')
        events = cPickle.load(tmp)
        tmp.close()
        return events
        
    def get_master_channel_list(self):
        """
        about:
            In the case that all files doe not have matching channel lists a 
            master channel list is used to provide a unique list over all files
        input:
            None
        return:
            a unique, sorted set of channels for all files in a project
        """

        allChannels = []
        fileList = get_fcs_file_names(self.homeDir)
        for fileName in fileList:
            fileChannels = self.get_file_channel_list(fileName)

            allChannels+=fileChannels
        allChannels = np.sort(np.unique(allChannels))

        ## remove white space
        allChannels = [re.sub("\s+","-",c) for c in allChannels]

        return allChannels

    def get_master_channel_indices(self,channels):
        """
        about:
            Returns the indices of given channels w.r.t. the master channel list.
        input:
            channels - a list (or other iterable) of channel names
        return:
            a list of channel indices
        """

        masterList = self.get_master_channel_list()
        channelInds = [np.where(np.array(masterList) == c)[0][0] for c in channels]
        
        return channelInds
   
    def get_file_channel_list(self,fileName):
        """
        about:
            Fetches the channels associated with a given file from a saved pickle file.
        input:
            fileName - string representing the file without the full path and without a file extension
        return:
            A np.array of file channels associated with a given file. The function returns None if 
            no channel list has yet been made.
        """
                
        fileName = fileName + "_channels_" + "original" + ".pickle"
        if os.path.isfile(os.path.join(self.homeDir,'data',fileName)) == False:
            print "INPUT ERROR: bad file name specified in model.get_file_channel_list"
            print "\t" + os.path.join(self.homeDir,'data',fileName)
            return None
        
        tmp = open(os.path.join(self.homeDir,'data',fileName),'rb')
        fileChannels = cPickle.load(tmp)
        tmp.close()
        fileChannels = np.array([re.sub("\s","_",c) for c in fileChannels])

        return fileChannels

    def get_subsample_indices(self,subsample,dataType='fcs'):
        """
        about:
            Creates a subsample of fcs data.  Subsample is a number smaller than the number of events 
            in the smallest file.  If it is not then subsample is saved as   
        args:    
            fileName - string representing the file without the full path and without a file extension
            dataType - may be any of the following: fcs,txt
        return:
            false when subsample size is larger than the number of 
            events in at least one of the project files.
        """

        if subsample == "original":
            return None

        subsample = int(float(subsample))

        ## use pickle file if already created
        if os.path.isfile(os.path.join(self.homeDir,'data','subsample_%s.pickle'%subsample)) == True:
            tmp = open(os.path.join(self.homeDir,'data','subsample_%s.pickle'%subsample),'rb')
            subsampleIndices = cPickle.load(tmp)
            tmp.close()
            return subsampleIndices

        ## otherwise create the pickle file
        fileList = get_fcs_file_names(self.homeDir)
        minNumObs = np.inf

        ## get minimum number of observations out of all files considered
        for fileName in fileList:
            fcsData = self.get_events(fileName,subsample='original')
            n,d = np.shape(fcsData)

            if n < minNumObs:
                minNumObs = n

            ## check to see that the specified subsample is <= the number of events
            if subsample > minNumObs:
                print "WARNING: subsample greater than minimum num events in file --- using all events", fileName
                subsample = minNumObs
           
        ## get the random ints and save as a pickle
        randEvents = np.random.random_integers(0,minNumObs-1,subsample)
        tmp = open(os.path.join(self.homeDir,'data','subsample_%s.pickle'%subsample),'w')
        cPickle.dump(randEvents,tmp)
        tmp.close()
        return randEvents

    def create_imgs_for_thumbnails(self,indexI,indexJ,fileName,subsample,imgDir,longModelName,modelName,modelType):
        """
        about:
            handler function for RunMakeFigures.
        args:
            indexI,indexJ,fileName,subsample,imgDir,longModelName,modelName,modelType
        return:
            None
        """

        script = os.path.join(self.baseDir,"RunMakeFigures.py")
        
        ## error checking
        if os.path.isfile(script) == False:
            print 'ERROR: cannot find RunMakeFigures'
        else:
            pltCmd = "%s %s -p %s -i %s -j %s -f %s -s %s -a %s -m %s -t %s -h %s"%(self.pythonPath,script,self.projectID,indexI,indexJ,fileName,subsample,
                                                                                    imgDir,longModelName,modelType,self.homeDir)
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

    def load_model_results_pickle(self,modelName,modelType):
        """
        about:
            loads a pickled fcm file into the workspace
        args:
            modelName - 
            modelType - must be one of the following: components, modes
        return:
            model and classify
        """
        
        if modelType not in ['components','modes']:
            print "ERROR: invalide model type specified in load_model_results"
            return False

        tmp1 = open(os.path.join(self.homeDir,'models',modelName+"_%s.pickle"%modelType),'r')
        tmp2 = open(os.path.join(self.homeDir,'models',modelName+"_classify_%s.pickle"%modelType),'r')
        model = cPickle.load(tmp1)
        samplesFromPostr = 1.0
        k = int(model.pis().size / samplesFromPostr)
        
        classify = cPickle.load(tmp2)
        tmp1.close()
        tmp2.close()

        return model,classify
    
    def get_n_color_colorbar(self,n,cmapName='jet'):
        """
        about:
            breaks any matplotlib cmap into n colors 
        args:
            cmapName - may be any mpl cmap i.e. spectral, jet, gist_rainbow
        return:
            a matplotlib.cmap
        """
        cmap = cm.get_cmap(cmapName,n) 
        return cmap(np.arange(n))

    def rgb_to_hex(self,rgb):
        """
        about:
            converts a rgb 3-tuple into hex
        args:
            3-tubple of red, green and blue numeric values
        return:
            hex color
        """

        return '#%02x%02x%02x' % rgb[:3]
