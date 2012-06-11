#!/usr/bin/python
'''
The base class for all model runs

'''

__author__ = "A. Richards"

import sys,getopt,os,re,cPickle,time,csv
import numpy as np
from cytostream import Logger,Model

class RunModelBase(object):

    def __init__(self,homeDir):

        ## error checking
        if os.path.isdir(homeDir) == False:
            print "INPUT ERROR: RunModelBase - invalid project", homeDir
            return None

        self.homeDir = homeDir
        self.projName = os.path.split(homeDir)[-1]
        self.projectID = os.path.split(homeDir)[-1]

        ## initialize a logger and a model to get specified files and channels
        self.log = Logger()
        self.log.initialize(homeDir,load=True)
    
        ## prepare model
        self.model = Model()
        self.model.initialize(homeDir)
        self.modelRunID = self.log.log['selected_model']
        self.subsample = self.log.log['subsample_run']

        ## get events
        try:
            self.subsample = str(int(float(self.subsample)))
        except:
            pass

        ## account for excluded channels
        self.excludedChannels = self.log.log['excluded_channels_analysis']
        if len(self.log.log['alternate_channel_labels']) == 0:
            self.fileChannels = self.model.get_master_channel_list()
        else:
            self.fileChannels = self.log.log['alternate_channel_labels']

        if len(self.excludedChannels) != 0:
            self.includedChannels = list(set(range(len(self.fileChannels))).difference(set(self.excludedChannels)))
            self.includedChannelLabels = np.array(self.fileChannels)[self.includedChannels].tolist()
            self.excludedChannelLabels = np.array(self.fileChannels)[self.excludedChannels].tolist()
        else:
            self.includedChannels = range(len(self.fileChannels))
            self.includedChannelLabels = self.fileChannels
            self.excludedChannelLabels = []

        if len(self.includedChannels) + len(self.excludedChannels) != len(self.fileChannels):
            print "ERROR: RunModelBase - Failed error sum check for excluding channels", len(self.includedChannels) + len(self.excludedChannels), len(self.fileChannels)
        elif type(self.includedChannels) != type([]) or type(self.excludedChannels) != type([]):
            print "ERROR: RunModelBase - Failed error type check for excluding channels", type(self.includedChannels),type(self.excludedChannels)

    def remove_border_events(self,events):
        '''
        remove the border data points for the model fitting                                                 '''
    
        n,d = np.shape(events)

        allZeroInds = []
        for ind in range(d):
            zeroInds = np.where(events[:,ind] == 0)
            zeroInds = zeroInds[0].tolist()
            if len(zeroInds) > 0:
                allZeroInds += zeroInds

        allZeroInds = list(set(allZeroInds))
        nonZeroInds = list(set(np.arange(n)).difference(set(allZeroInds)))

        if len(allZeroInds) + len(nonZeroInds) != n:
            print "ERROR: RunDPMM.py Failed clean borders integrity check"

        return events[nonZeroInds,:]

    def start_timer(self):
        '''
        starts time for model run
        '''

        self.modelRunStart = time.time()
    
    def get_run_time(self):
        '''
        ends timer for model and returns runtime
        '''
    
        self.modelRunStop = time.time()
        return self.modelRunStop - self.modelRunStart

    def list2Str(self,lst):
        strList =  "".join([str(i)+";" for i in lst])[:-1]
        if strList == '':
            return '[]'
        else:
            return strList
