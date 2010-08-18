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
> indices = model.get_subsample_indices('1e3')

Adam Richards
adam.richards@stat.duke.edu
"""
import sys,csv,os,re,cPickle
sys.path.append("/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages")
import fcm
import fcm.statistics
import numpy as np
from FileControls import get_fcs_file_names,get_img_file_names,get_models_run,get_project_names

from matplotlib import rc
import matplotlib.cm as cm
rc('font',family = 'sans-serif')
#rc('text', usetex = True)

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
        Basic constructor method.  Class must be initialized before use. 

        """
        self.projectID = None
        self.homeDir = None

    def initialize(self,projectID,homeDir):
        """
        Associates a class with a project and home directory

        """
        self.projectID = projectID
        self.homeDir = homeDir
    
    def pyfcm_load_fcs_file(self,fileName,compensationMatrix=None):
        """
        returns a fcm data object
        fileName is a fcs file name associated with a project

        """      
        fullFileName = os.path.join(self.homeDir,"data",fileName)
        data = fcm.loadFCS(fullFileName)
        return data

    def get_master_channel_list(self):
        """
        returns a unique, sorted set of channels for all files in a project

        """

        allChannels = set()
        fileList = get_fcs_file_names(self.homeDir)
        for fileName in fileList:
            data = self.pyfcm_load_fcs_file(fileName)
            allChannels.update(data.channels)

        ## remove white space and sort
        allChannels = [re.sub("\s","-",c) for c in allChannels]
        allChannels.sort()

        return allChannels

    def get_master_channel_indices(self,channels):
        """
        returns the indices of given channels w.r.t. the master channel list
        channels is a iteriable

        """

        masterList = self.get_master_channel_list()
        channelInds = [np.where(np.array(masterList) == c)[0][0] for c in channels]
        
        return channelInds
   
    def get_file_channel_list(self,fileName):
        """
        returns the channels associated with a given file
        fileName is not the path but the fcs file name

        """

        data = self.pyfcm_load_fcs_file(fileName)
        channels = data.channels
        channels = [re.sub("\s","-",c) for c in channels]
        return channels

    def get_subsample_indices(self,subsample):
        """
        get subsample indices
        subsample is a number smaller than the number of events in the smallest file
        method returns false when subsample size is larger than the number of 
        events in at least one of the project files.
   
        """

        self.subsample = subsample

        if self.subsample == "All Data":
            return None
        
        subsample = int(float(subsample))
        fileList = get_fcs_file_names(self.homeDir)
        numObs = None
        minNumObs = np.inf

        ## get minimum number of observations out of all files considered
        for file in fileList:
            data = self.pyfcm_load_fcs_file(file)
            n,d = np.shape(data)
                
            ## curiousity check
            if numObs == None:
                numObs = n
            elif numObs != n:
                pass
                #print "INFO: number of observations are not equal for at least two files"
                    
            if n < minNumObs:
                minNumObs = n

            if subsample > minNumObs:
                print "ERROR: subsample greater than minimum num events in file", file
                return False

        ## get the random integers
        np.random.seed(42)
        return np.random.random_integers(0,minNumObs-1,subsample)
             
    def load_model_results_pickle(self,modelName,modelType):
        """
        loads a pickled fcm file into the workspace
        data is a fcm data object
        k is the number of components
        the results are the last 5 samples from the posterior so here we average those samples then 
        use those data as a summary of the posterior
        """
        
        if modelType not in ['components','modes']:
            print "ERROR: invalide model type specified in load_model_results"
            return False

        tmp1 = open(os.path.join(self.homeDir,'models',modelName+"_%s.pickle"%modelType),'r')
        tmp2 = open(os.path.join(self.homeDir,'models',modelName+"_classify_%s.pickle"%modelType),'r')
        model = cPickle.load(tmp1)
        samplesFromPostr = 1.0
        k = int(model.pis().size / samplesFromPostr)
        #print 'calculated k = ', k
        #print 'pi', np.shape(model.pis())
        #print 'mu', np.shape(model.mus()), np.shape(model.mus()[0])
        #print 'sig',np.shape(model.sigmas()), np.shape(model.sigmas()[0])

        # working on the averaging thing
        #newPis = np.reshape(model.pis(),(k,samplesFromPostr))
        #newPis = np.mean(newPis,axis=1)
        #allsamples, features = np.shape(model.mus())
        #newMus = None
        #for d in range(features):
        #    newMusD = np.reshape(model.mus()[:,d],(k,samplesFromPostr))
        #    newMusD = np.mean(newMusD,axis=1)
        #    if newMus == None:
        #        newMus = newMusD
        #    else:
        #        newMus = np.vstack([newMus,newMusD])
        #newMus = newMus.transpose()
    
        # alternative is to just take one of the occurances of each
        #newPis = model.pis()[:k]
        #newMus =  model.mus()[:k,:]
        #newSigmas = model.sigmas()[:k,:,:]
        #print np.shape(newPis), np.shape(newMus), np.shape(newSigmas)
        
        #model.pis = newPis
        #model.mus = newMus
        #model.sigmas = newSigmas
        
        classify = cPickle.load(tmp2)
        tmp1.close()
        tmp2.close()

        return model,classify
    
    def get_n_color_colorbar(self,n,cmapName='jet'):# Spectral #gist_rainbow
        "breaks any matplotlib cmap into n colors" 
        cmap = cm.get_cmap(cmapName,n) 
        return cmap(np.arange(n))

    def rgb_to_hex(self,rgb):
        """
        converts a rgb 3-tuple into hex
        """

        return '#%02x%02x%02x' % rgb[:3]
