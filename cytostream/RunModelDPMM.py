#!/usr/bin/python
'''
run the kmeans model on a given file
'''

__author__ = 'A. Richards'

import sys,getopt,os,re,cPickle,time,csv
import numpy as np
from RunModelBase import RunModelBase
import fcm
import fcm.statistics

if len(sys.argv) < 3:
    print sys.argv[0] + " -f fileName -h homeDir -v -g gpuDevice"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:h:g:c:v')
except getopt.GetoptError:
    print sys.argv[0] + "-f fileName -h homeDir -g gpuDevice[optional]"
    print " Note: fileName (-f) must be the full" 
    print " homeDir  (-h) home directory for current project"
    print " gpuDevice     (-k) device id for gpu"
    print " verbose       (-v) verbose flag"
    sys.exit()

name = None
verbose = False
gpuDevice = 0
for o, a in optlist:
    if o == '-f':
        fileName = a
    if o == '-h':
        homeDir = a
    if o == '-v':
        verbose = True
    if o == '-g':
        gpuDevice = int(a)

class RunModelDPMM(RunModelBase):

    def __init__(self,homeDir):
        RunModelBase.__init__(self,homeDir)
        
    def run(self):
        '''
        run specified model
        '''

        #print '\t\trunning %s %s',fileName,gpuDevice

        if verbose == True:
            print '\t...writing log file',os.path.split(__file__)[-1]

        ## persistant parameters
        selectedModel = self.log.log['model_to_run']
        subsample = self.subsample
        modelMode = self.log.log['model_mode']
        modelRunID = self.modelRunID
        modelReference = self.log.log['model_reference']
        modelReferenceRunID =  self.log.log['model_reference_run_id']
        includedChannels = self.includedChannels

        ## model specific parameters
        cleanBorderEvents = True
        k = int(self.log.log['dpmm_k'])
        dpmmGamma = float(self.log.log['dpmm_gamma'])
        nIters =  int(self.log.log['dpmm_niter'])
        burnin =  int(self.log.log['dpmm_burnin'])

        ## prepare events
        events = self.model.get_events_from_file(fileName)
        if subsample != 'original':
            subsampleIndices = self.model.get_subsample_indices(subsample)
            events = events[subsampleIndices,:]

        events = events[:,includedChannels]
        if cleanBorderEvents == True:
            nonBorderEvents = self.remove_border_events(events)

        ## initialize model
        self.start_timer()
        
        mod = fcm.statistics.DPMixtureModel(nclusts=k,niter=nIters,burnin=burnin)
        mod.gamma = dpmmGamma

        ## gpu settings
        mod.device = [gpuDevice]
        #print 'value gpu device', gpuDevice
        
        ## fit the model
        if cleanBorderEvents == True:
            full = mod.fit(nonBorderEvents,verbose=True)
        else:
            full = mod.fit(events,verbose=True)
                
        ## niter is number of iters saved and burnin is the number to do before saving
        mod = fcm.statistics.DPMixtureModel(nclusts=k,niter=nIters,burnin=burnin)
        mod.gamma = dpmmGamma

        ## older functions used to load saved parameters (deprecated)
        #mod.load_mu(refMod.mus())
        #mod.load_sigma(refMod.sigmas())
        #mod.load_pi(refMod.pis())
        #full = mod.fit(nonBorderEvents,verbose=True)
    
        ## classification
        classifyStart = time.time()
        componentLabels = full.classify(events)
        print componentLabels.shape
        classifyEnd = time.time()
        classifyTime = classifyEnd - classifyStart
        runTime = self.get_run_time()
        
        ## save cluster labels (components)
        self.model.save_labels(fileName,componentLabels,modelRunID)

        ## save modes
        #modes = full.make_modal()
        #classifyModes = modes.classify(events)
        #self.model.save_labels(self,fileName,classifyComponents,modelRunID)
        
        ## save a log file
        if verbose == True:
            print '\t...writing log file', os.path.split(__file__)[-1]

        ## save a log file
        logDict = self.get_labels_log()

        ## add general info to the log file
        logDict["subsample"]        = str(subsample)
        logDict["file name"]        = fileName
        logDict["full model name"]  = re.sub('"',"",self.model.modelsInfo[selectedModel][0]),
        logDict["total runtime"]    = time.strftime('%H:%M:%S', time.gmtime(runTime))
        logDict["model runtime"]    = time.strftime('%H:%M:%S', time.gmtime(runTime-classifyTime))
        logDict["classify runtime"] = time.strftime('%H:%M:%S', time.gmtime(classifyTime))
        logDict["number events"]    = str(events.shape[0])
        logDict["model mode"]       = modelMode
        
        ## add model specific values for the logfile
        logDict["number components"] = str(k)
        logDict["dpmm gamma"]        = str(dpmmGamma)
        logDict["dpmm nIters"]       = str(nIters)
        logDict["dpmm burnin"]       = str(burnin)

        ## save the logfile
        self.model.save_labels_log(fileName,logDict,modelRunID)

if __name__ == '__main__':
    runModel = RunModelDPMM(homeDir)
    runModel.run()
