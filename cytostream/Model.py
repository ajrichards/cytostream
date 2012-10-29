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

import ast,sys,csv,os,re,cPickle,subprocess,time
import matplotlib as mpl

if mpl.get_backend() != 'agg':
    mpl.use('agg')

import numpy as np
from FileControls import get_fcs_file_names,get_img_file_names,get_project_names
from ModelsInfo import modelsInfo
from matplotlib import rc
import matplotlib.cm as cm
from PyQt4 import QtCore, QtGui
rc('font',family = 'sans-serif')

import warnings
  
class Model:
    """ 
    Class to carry out interfacing with data files and fcm library
    class is first created then initialized
        
    syntax:
        model = Model()
        model.initialize(projectID, homeDir)
    """

    def __init__(self,verbose=False):
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
        self.verbose = verbose

        ## get base directory 
        if hasattr(sys, 'frozen'):
            self.baseDir = os.path.dirname(sys.executable)
            self.baseDir = re.sub("MacOS","Resources",self.baseDir)
        else:
            self.baseDir = os.path.dirname(__file__)

        ## set python path
        pathsToTry = ["/opt/local/bin/python",
                      "/usr/local/bin/python",
                      "/usr/bin/python"]
        pythonPath = None
        for path in pathsToTry:
            if os.path.exists(path):
                pythonPath = path
                break
        
        if pythonPath != None: 
            if os.path.exists(pythonPath) == False:
                print "ERROR: bad specified python path in config.py... using default", pythonPath
                self.pythonPath = os.path.join(os.path.sep,"usr","bin","python")
            else:
                self.pythonPath = pythonPath
        elif sys.platform == 'win32':
            self.pythonPath = os.path.join("C:\Python27\python")
        else:
            self.pythonPath = os.path.join(os.path.sep,"usr","bin","python")

        ## add global variables
        self.modelsInfo = modelsInfo

    def initialize(self,homeDir):
        """
        about:
            Associates a class with a project and home directory. The function
            also sets the python path.
        input:
            homeDir - is the full path for the home dir including the projectID
        return:
            None
        """

        ## initialize project
        self.projectID = os.path.split(homeDir)[-1]
        self.homeDir = homeDir
            
    def load_files(self,fileList,dataType='fcs',transform='log',progressBar=None,fileChannelPath=None,
                   autoComp=True,compensationFilePath=None,logicleScaleMax=262144):
        """
        about: 
            This is a handler function for the script LoadFile.py which loads an fcs
            or txt file of flow cytometry data.  For the binary fcs normally this is 
            carried out using the fcm python module.  This method is called by
            controlller.load_files_handler.
        input:
            fileList - a list of full paths, or a list of array objects
            dataType - may be any of the following: fcs,comma,tab,array
            transform - may be any of the follwing: log, logicle 
        return:
            None
        """

        ## error checking
        if type(fileList) != type([]):
            print "INPUT ERROR: Model -- load_files: takes as input a list of file paths"
            return None
        if os.path.isdir(self.homeDir) == False:
            os.mkdir(self.homeDir)
            os.mkdir(os.path.join(self.homeDir,"data"))
            print "INFO: making home dir from Model"

        if dataType in ['comma','tab'] and fileChannelPath==None:
            print "ERROR: Model -- if data input type is comma|tab you must specify the fileChannelPath"
            print "\t data type was", dataType
            return None

        ## create script
        script = os.path.join(self.baseDir,"LoadFile.py")

        fileCount = 0
        for filePath in fileList:
            if self.verbose == True:
                print 'loading %s...'%filePath
            if progressBar != None:
                progressBar.progressLabel.setText("loading %s..."%os.path.split(filePath)[-1])

            if compensationFilePath == "None":
                pass
            elif compensationFilePath == None:
                compensationFilePath = "None"
            else:
                if os.path.exists(compensationFilePath) == False:
                    print "ERROR: Model -- bad compensation file path specified", compensationFilePath
                    compensationFilePath = "None"

            ## if data is of type array
            if dataType == 'array':
                fileChannels = fileChannelPath
                data = filePath
                existingFiles = get_fcs_file_names(self.homeDir)
                numFiles = len(existingFiles)
                newDataFileName = 'array'+ str(numFiles+1) + "_data.npy"
                newDataFilePath = os.path.join(self.homeDir,'data',newDataFileName)
                newChanFileName = 'array'+ str(numFiles+1) + "_channels.pickle"
                newChanFilePath = os.path.join(self.homeDir,'data',newChanFileName)
                
                ## write
                np.save(newDataFilePath,data)
                fileChannels = [chan for chan in fileChannels]
                tmp = open(newChanFilePath,'w')
                cPickle.dump(fileChannels,tmp)
                tmp.close()
            else:
                cmd = "'%s' '%s' -f '%s' -h '%s' -d '%s' -t '%s' -c '%s' -m '%s' -a '%s' -l '%s'"%(self.pythonPath,script,filePath,self.homeDir,dataType,
                                                                                                   transform,fileChannelPath,compensationFilePath,autoComp,
                                                                                                   logicleScaleMax)

                proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
                ## for debugging
                #proc = subprocess.Popen(cmd,shell=True)
                
                while True:
                    try:
                        next_line = proc.stdout.readline()
                        if next_line == '' and proc.poll() != None:
                            break
                        ## to debug uncomment the following line
                        print next_line
                    except:
                        break
            
                proc.wait()

            fileCount+=1
            percentDone = float(fileCount) / float(len(fileList)) * 100.0
             
            if progressBar != None:
                progressBar.move_bar(int(round(percentDone)))
                progressBar.show()
                QtCore.QCoreApplication.processEvents()

            ## check to see that files were made
            newFileName = re.sub('\s+','_',os.path.split(filePath)[-1])
            newFileName = re.sub('\.fcs|\.txt|\.out','',newFileName)
            newDataFileName = newFileName +"_data.npy"
            newChanFileName = newFileName +"_channels.pickle"
            if os.path.isfile(os.path.join(self.homeDir,'data',newDataFileName)) == False:
                print "ERROR: data file was not successfully created", os.path.join(self.homeDir,'data',newDataFileName)
            if os.path.isfile(os.path.join(self.homeDir,'data',newChanFileName)) == False:
                print "ERROR: channel file was not successfully created", os.path.join(self.homeDir,'data',newChanFileName)

    def get_events_from_file(self,fileName,fileDir=None):
        """
        about:
            this function handles the fetching of the events associated with a given file.
        input:
            fileName - may be a fileName from the fileName list or it may be a link to a pickle file elsewhere
        return:
            a np.array of event data
        """
        
        fileList = get_fcs_file_names(self.homeDir)

        if fileName not in fileList and fileDir != None:
            if os.path.isdir(fileDir) == False:
                print "ERROR: Model.get_events_from_pickle -- Invalid fileDir specified"
                return None
            originalFilePath = os.path.join(fileDir,fileName + "_data.npy")
        else:
            originalFilePath = os.path.join(self.homeDir,'data',fileName + "_data.npy")

        ## error check
        if os.path.exists(originalFilePath) == False:
            print "ERROR: Model.get_events_from_file -- Specified events pickle does not exist"
            print originalFilePath
            return None

        
        ## load events using pickle
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            events = np.load(originalFilePath)

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

        if len(fileList) == 0:
            return allChannels

        allChannels = self.get_file_channel_list(fileList[0])

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

        fileChannelsPath = os.path.join(self.homeDir,'data',fileName + "_channels.pickle")
        if os.path.isfile(fileChannelsPath) == False:
            print "INPUT ERROR: bad file name specified in model.get_file_channel_list"
            print "\t" + fileChannelsPath
            return None
        
        tmp = open(fileChannelsPath,'r')
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

        if not re.search('filter',str(subsample)):
            subsample = int(float(subsample))

        ## use pickle file if already created
        sampleIndicesFilePath = os.path.join(self.homeDir,'data','subsample_%s.npy'%subsample)        
        if os.path.isfile(sampleIndicesFilePath) == True:
            subsampleIndices = np.load(sampleIndicesFilePath)
            if self.verbose == True:
                print 'INFO: using pickled subsampled indices'

            return subsampleIndices

        ## otherwise create the pickle file
        fileList = get_fcs_file_names(self.homeDir)
        minNumEvents = np.inf

        ## error checking
        if len(fileList) == 0:
            print "ERROR: cannot carry out subsampling -- no files in file list"
            return None

        ## get minimum number of observations out of all files considered
        for fileName in fileList:
            fcsData = self.get_events_from_file(fileName)
            n,d = np.shape(fcsData)
        
            if n < minNumEvents:
                minNumEvents = n
        
        ## handle subsampling 
        if type(0) == type(subsample):
            if subsample < minNumEvents:
                ssSize = subsample
            else:
                ssSize = n

            randEvents = np.arange(minNumEvents)
            np.random.shuffle(randEvents)
            randEvents = randEvents[:subsample]
        else:
            print "WARNING: Model.py get_sumsample_indices -- subsample must be the array or an int -- using original data"
            return None

        ## save rand events for future use
        np.save(sampleIndicesFilePath,randEvents)

        return randEvents

    def save_labels(self,fileName,fileLabels,labelsID):
        """
        saves labels as a numpy array object for a given file name
        """

        if type(fileLabels) == type([]):
            fileLabels = np.array(fileLabels)

        saveFilePath = os.path.join(self.homeDir,'models',fileName+"_%s"%(labelsID)+".npy")
        if os.path.exists(saveFilePath):
            print "ERROR: Model.save_labels -- labels file already exists skipping"
            return

        np.save(saveFilePath,fileLabels)

    def save_labels_log(self,fileName,logDict,labelsID):
        """
        saves label log as a human readable csv file
        """

        logFilePath = os.path.join(self.homeDir,'models',fileName+"_%s"%(labelsID)+".log")
        if os.path.exists(logFilePath):
            print "ERROR: Model.save_labels_log -- labels file already exists skipping"
            return
        
        fid = open(logFilePath,"w")
        writer = csv.writer(fid)   

        for key,item in logDict.iteritems():
            if item == None:
                item = 'None'
            elif type(item) != type('i am a string'):
                item = str(item)

            writer.writerow([key,item])

        fid.close()

    def load_saved_labels(self,fileName,labelsID):
        """
        loads labels that have been saved by cytostream
        returns the labels in the form of a np.array
        """

        saveFilePath = os.path.join(self.homeDir,'models',fileName+"_%s"%(labelsID)+".npy")

        if os.path.isfile(saveFilePath) == False:
            print "ERROR: Model cannot load labels -- file does not exist"
            print "...", saveFilePath
            return None

        ## load the labels
        tmp = open(saveFilePath,'r')
        fileLabels = np.load(tmp)
        tmp.close()

        return fileLabels
    
    def load_saved_labels_log(self,fileName,labelsID):
        """
        loads the log file that is associated with a labelsID 
        returns the log in the form of a dictionary
        """
        
        print 'loading saved labels log...', fileName, labelsID
        tmpFile = os.path.join(self.homeDir,'models',fileName+"_%s"%(labelsID)+".log")
        if os.path.isfile(tmpFile) == False:
            return None

        logFileDict = {}
        reader = csv.reader(open(tmpFile,'r'))
        for linja in reader:
            item = linja[1]
            if re.search("\[|\{|None",str(item)):
                item = ast.literal_eval(str(item))

            logFileDict[linja[0]] = item

        return logFileDict

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


    def save_channel_dict(self,channelDict):
        '''
        save the channelDict for future use
        '''

        if channelDict == None:
            print "WARNING: Model.save_channel_dict -- cannot save a None channel dict"
            return None

        tmp = open(os.path.join(self.homeDir,'data','channelDict.pickle'),'w')
        cPickle.dump(channelDict,tmp)
        tmp.close()

    def load_channel_dict(self):
        '''
        load the channel dict
        '''

        filePath = os.path.join(self.homeDir,'data','channelDict.pickle')

        if os.path.exists(filePath) == False:
            return None

        tmp = open(filePath,'rb')
        channelDict = cPickle.load(tmp)
        tmp.close()

        return channelDict

    def save_filter_indices(self,fileName,parentModelRunID,modelMode,filterIndices,filterID):
        ## check to see if a log file has been created for this project
        filterLogFile = os.path.join(self.homeDir,"data",'%s_%s.log'%(fileName,filterID))
        if os.path.isfile(filterLogFile) == True:
            filterLog = csv.writer(open(filterLogFile,'a'))
        else:
            filterLog = csv.writer(open(filterLogFile,'w'))

        indicesFilePath = os.path.join(self.homeDir,"data",'%s_%s.npy'%(fileName,filterID))
        np.save(indicesFilePath,filterIndices)

        filterLog.writerow([fileName,"timestamp", time.asctime()])
        filterLog.writerow([fileName,"parent model run",parentModelRunID])
        filterLog.writerow([fileName,"model mode",modelMode])
        if type(filterIndices) == type(np.array([])):
            filterLog.writerow([fileName,'filter size',str(filterIndices.shape[0])])
        else:
            filterLog.writerow([fileName,'filter size','0'])

    def load_filter(self,fileName,filterID):
        indicesFilePath = os.path.join(self.homeDir,"data",'%s_%s.npy'%(fileName,filterID))
        if os.path.exists(indicesFilePath) == False:
            print "WARNING: Model.load_filter -- cannot load filter path does not exist"
            print "...", indicesFilePath
            return []
        
        filterIndices = np.load(indicesFilePath)
        return filterIndices

    def get_filter_indices_by_clusters(self,fileName,parentModelRunID,modelMode,clusterIDs):
        '''
        given a set of cluster ids (list) the respective events indices are found and returned
        always returns indices with respect to original data

        '''

        if len(clusterIDs) == 0:
            print "WARNING: Controller.get_indices_for_filter -- clusterIDs was empty"
            return None

        statModel, fileLabels = self.load_model_results_pickle(fileName,parentModelRunID,modelType=modelMode)
        modelLog = self.load_model_results_log(fileName,parentModelRunID)
        parentSubsample = modelLog['subsample']
                
        ## get events
        #events = self.get_events(fileName,subsample=parentSubsample)
        
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
       
        ## if subsample was used get indices in terms of original data
        if parentSubsample != 'original':
            #events = self.get_events(fileName,subsample=parentSubsample)
            #origLabels = np.arange(0,events.shape[0])
            parentSubsampleIndices = self.get_subsample_indices(parentSubsample)
            filterIndices = parentSubsampleIndices[filterIndices]

        return filterIndices
