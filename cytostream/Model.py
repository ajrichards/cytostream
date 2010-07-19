#!/usr/bin/env python
'''

'''
import tkMessageBox,tkSimpleDialog,csv,os,re,cPickle
import fcm
import fcm.statistics
import numpy as np
import Tkinter as tk
from FileControls import *

## matplotlib imports and configs
#from matplotlib.ticker import NullFormatter,MaxNLocator
#from matplotlib import pyplot
#from matplotlib.figure import Figure

## this prevents windows from popping up for each figure generation
import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot
from matplotlib import rc
import matplotlib.cm as cm
rc('font',family = 'sans-serif')
#rc('text', usetex = True)

class Model:

    def __init__(self):
        self.projectID = None
        self.homeDir = None

    def initialize(self,projectID,homeDir):
        self.projectID = projectID
        self.homeDir = homeDir
    
    # returns a fcm data object
    # fileName is a fcs file name associated with a project
    def pyfcm_load_fcs_file(self,fileName,compensationMatrix=None):
        fullFileName = os.path.join(self.homeDir,"data",fileName)
        data = fcm.loadFCS(fullFileName)
        return data

    ## returns a unique, sorted set of channels for all files in a project
    ##
    def get_master_channel_list(self):
        allChannels = set()
        fileList = get_fcs_file_names(self.homeDir)
        for fileName in fileList:
            data = self.pyfcm_load_fcs_file(fileName)
            allChannels.update(data.channels)

        ## remove white space and sort
        allChannels = [re.sub("\s","-",c) for c in allChannels]
        allChannels.sort()

        return allChannels


    # returns the indices of given channels w.r.t. the master channel list
    # channels is a iteriable
    def get_master_channel_indices(self,channels):
        masterList = self.get_master_channel_list()
        channelInds = [np.where(np.array(masterList) == c)[0][0] for c in channels]
        
        return channelInds
   
    # returns the channels associated with a given file
    # fileName is not the path but the fcs file name
    #
    def get_file_channel_list(self,fileName):
        data = self.pyfcm_load_fcs_file(fileName)
        channels = data.channels
        channels = [re.sub("\s","-",c) for c in channels]
        return channels

    # get subsample indices
    # subsample is a number smaller than the number of events in the smallest file
    #
    def get_subsample_indices(self,subsample):
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

        ## get the random integers
        np.random.seed(42)
        return np.random.random_integers(0,minNumObs-1,subsample)
             
    ### loads the a pickled fcm file into the workspace
    # data is a fcm data object
    # k is the number of components
    # the results are the last 5 samples from the posterior so here we average those samples then 
    # use those data as a summary of the posterior
    def load_model_results_pickle(self,modelName):
        tmp1 = open(os.path.join(self.homeDir,'models',modelName+".pickle"),'r')
        tmp2 = open(os.path.join(self.homeDir,'models',modelName+"_classify.pickle"),'r')
        model = cPickle.load(tmp1)
        samplesFromPostr = 5.0

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
    
    def make_scatter_plot_with_histograms(self,file1,channel1tuple,channel2tuple,buff=0.02,labels=None,histograms=False,alpha=0.75,transparent=True):
        #fig = pyplot.figure(figsize=(10,7.5))
        #ax = fig.add_subplot(111)

        nullfmt   = NullFormatter()         # no labels
        plotType = 'png'
        fontSize = 12
        channel1,index1 = channel1tuple
        channel2,index2 = channel2tuple
        colors = ['blue','orange','black','green','red','yellow','magenta','cyan']
        data = self.pyfcm_load_fcs_file(file1)
        
        ## subset give an numpy array of indices
        if self.controller.subsampleIndices != None:
            data = data[self.controller.subsampleIndices,:]
        else:
            data = data[:,:]

        ## error checking  
        if type(labels) == type([]):
            labels = np.array(labels)

        x = data[:,index1]
        y = data[:,index2]
        
        # definitions for the axes 
        left, width = 0.1, 0.65
        bottom, height = 0.1, 0.65
        bottom_h = left_h = left+width+0.02

        rect_scatter = [left, bottom, width, height]
        rect_histx = [left, bottom_h, width, 0.2]
        rect_histy = [left_h, bottom, 0.2, height]

        # start with a rectangular Figure
        fig = pyplot.figure(figsize=(7,7))
        pyplot.figtext(0.8,0.9,'xaxis: %s'%channel1)
        pyplot.figtext(0.8,0.85,'yaxis: %s'%channel2)
        axScatter = pyplot.axes(rect_scatter)
        axHistx = pyplot.axes(rect_histx)
        axHisty = pyplot.axes(rect_histy)

        # labels
        axHistx.xaxis.set_major_formatter(nullfmt)
        axHisty.yaxis.set_major_formatter(nullfmt)

        # the scatter plot:
        if labels == None:
            axScatter.scatter([x],[y],color=colors[0])
        else:
            numLabels = len(list(set(labels)))

            for l in labels:
                x = data[:,index1][np.where(labels==l)]
                y = data[:,index2][np.where(labels==l)]

                if l == 999:
                    axScatter.scatter([x],[y],color='gray')
                else:
                    axScatter.scatter([x],[y],color=colors[l])

        ## handle data edge buffers
        bufferX = buff * (data[:,index1].max() - data[:,index1].min())
        bufferY = buff * (data[:,index2].max() - data[:,index2].min())
        axScatter.set_xlim([data[:,index1].min()-bufferX,data[:,index1].max()+bufferX])
        axScatter.set_ylim([data[:,index2].min()-bufferY,data[:,index2].max()+bufferY])
        axScatter.yaxis.set_major_locator(MaxNLocator(4))
        axScatter.xaxis.set_major_locator(MaxNLocator(4))

        axHistx.hist(x,color=colors[0],alpha=alpha)
        axHisty.hist(y, orientation='horizontal',color=colors[0],alpha=alpha)
        numTicks = 3
        axHistx.yaxis.set_major_locator(MaxNLocator(numTicks))
        axHisty.xaxis.set_major_locator(MaxNLocator(numTicks))

        ## plot configuration
        #pyplot.title("%s_%s"%(channel1,channel2),fontname=self.controller.fontName)
        fileName = os.path.join(self.controller.homeDir,'figs',"%s_%s_%s.%s"%(file1[:-4],channel1,channel2,plotType))
        fig.savefig(fileName,transparent=transparent,facecolor='black')

        ## memory cleanup
        axScatter.images = []
        axHistx.images = []
        axHisty.images = []
        del data
        pyplot.clf()

    def get_n_color_colorbar(self,n):
        cmap = cm.get_cmap('jet', n) # Spectral #gist_rainbow
        return cmap(np.arange(n))

    def rgb_to_hex(self,rgb):
        return '#%02x%02x%02x' % rgb[:3]

   

    #def map_indices_from_master_list_to_file_specific(self,file,indices):
    #    masterList = self.get_master_channel_list()
    #    selectedChannels = [masterList[i] for i in indices]
    #    fileChannels = self.get_file_channel_list(file)
    #    channelInds = [np.where(np.array(fileChannels) == c)[0][0] for c in selectedChannels]
    #    
    #    return channelInds
    
