#!/usr/bin/python
'''
run the kmeans model on a given file
'''

__author__ = 'A. Richards'

import sys,getopt,os,re,cPickle,time,csv
import numpy as np
from cytostream import RunModelBase
from cytostream.stats import SilValueGenerator
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

        if verbose == True:
            print '\t...writing log file',os.path.split(__file__)[-1]

        ## persistant parameters
        selectedModel = self.log.log['model_to_run']
        subsample = self.subsample
        modelMode = self.log.log['model_mode']
        modelNum = self.modelNum
        modelReference = self.log.log['model_reference']
        modelReferenceRunID =  self.log.log['model_reference_run_id']
        includedChannels = self.includedChannels

        ## model specific parameters
        cleanBorderEvents = True
        k = int(self.log.log['k'])
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

        ## run model
        self.start_timer()
        
        loadModel = False
        if modelMode == 'onefit' and modelReference == fileName:
            loadModel = False
        elif modelMode == 'onefit':
            loadModel = True

        loadParams = False
        forceFit = False
        if forceFit == True and modelReference == fileName:
            loadParams = False
        elif forceFit == True:
            loadParams = True

        if loadModel == False:
            if loadParams == False:
                mod = fcm.statistics.DPMixtureModel(nclusts=k,niter=nIters,burnin=burnin)
                mod.gamma = dpmmGamma

                ## handle gpu
                mod.device = gpuDevice
                if cleanBorderEvents == True:
                    full = mod.fit(nonBorderEvents,verbose=True)
                else:
                    full = mod.fit(events,verbose=True)
                #full = mod.get_results()
                tmp0 = open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_dpmm.pickle"),'w')
                cPickle.dump(full,tmp0)
                tmp0.close()
            else:
                tmp0 = open(os.path.join(homeDir,'models',modelReference+"_%s"%(modelNum)+"_dpmm.pickle"),'r')
                refMod = cPickle.load(tmp0)
                tmp0.close()
        
                ## niter is number of iters saved and burnin is the number to do before saving
                mod = fcm.statistics.DPMixtureModel(nclusts=k,niter=nIters,burnin=burnin)
                mod.gamma = dpmmGamma
                mod.load_mu(refMod.mus())
                mod.load_sigma(refMod.sigmas())
                mod.load_pi(refMod.pis())
                full = mod.fit(nonZeroEvents,verbose=True)
                #full = mod.get_results()
    
        ## use a saved model
        else:
            full, uselessClasses = self.model.load_model_results_pickle(modelReference,modelReferenceRunID,modelType='components')

        ## get components
        classifyComponents = full.classify(events)

        ## get modes
        #modes = full.make_modal()
        #classifyModes = modes.classify(events)

        runTime = self.get_run_time()
        ## save cluster labels (components)
        componentsFilePath = os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_components.npy")
        np.save(componentsFilePath,classifyComponents)
        tmp1 = open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_full.pickle"),'w')
        cPickle.dump(full,tmp1)
        tmp1.close()

        ## save cluster labels (modes)
        #modesFilePath = os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_modes.npy")
        #np.save(modesFilePath,classifyModes)

        ## save a log file
        if verbose == True:
            print '\t...writing log file', os.path.split(__file__)[-1]

        writer = csv.writer(open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+".log"),'w'))
        
        ## for all models
        writer.writerow(["timestamp", time.asctime()])
        writer.writerow(["subsample", str(subsample)])
        writer.writerow(["project id", self.projName])
        writer.writerow(["file name", fileName])
        writer.writerow(["full model name", re.sub('"',"",self.model.modelsInfo[selectedModel][0])])
        writer.writerow(["model runtime",str(round(runTime,4))])
        writer.writerow(["used channels",self.list2Str(self.includedChannelLabels)])
        writer.writerow(["unused channels",self.list2Str(self.excludedChannelLabels)])        
        writer.writerow(["number events",str(events.shape[0])])
        writer.writerow(["model mode", modelMode])
        writer.writerow(["dpmm gamma", str(dpmmGamma)])
        writer.writerow(["dpmm nIters", str(nIters)])
        writer.writerow(["dpmm burnin", str(burnin)])

        ## model specific
        writer.writerow(["number components",str(k)])

if __name__ == '__main__':
    print 'running RunModelDPMM.py...'
    runModel = RunModelDPMM(homeDir)
    runModel.run()
