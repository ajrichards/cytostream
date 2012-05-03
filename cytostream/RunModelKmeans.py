#!/usr/bin/python
'''
run the kmeans model on a given file
'''

__author__ = 'A. Richards'

import sys,getopt,os,re,cPickle,time,csv
import numpy as np
from cytostream import RunModelBase
from scipy.cluster.vq import kmeans2,kmeans
from cytostream.stats import SilValueGenerator

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

class RunModelKmeans(RunModelBase):

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
        cleanBorderEvents = False
        k = int(self.log.log['k'])
        repeats = int(self.log.log['kmeans_repeats'])

        ## prepare events
        events = self.model.get_events_from_file(fileName)
        if subsample != 'original':
            subsampleIndices = self.model.get_subsample_indices(subsample)
            events = events[subsampleIndices,:]

        events = events[:,includedChannels]
        if cleanBorderEvents == True:
            nonBorderEvents = self.clean_border_events(events)

        ## run model
        self.start_timer()
        
        bestRepeat = (None,None,-2.0)
        for repeat in range(repeats):
            
            try:
                kmeanResults, kmeanLabels = kmeans2(events,k,minit='points')
                svg = SilValueGenerator(events,kmeanLabels)
                avgSilVal = svg.silValues.mean()
            except:
                kmeanResults = None

            if kmeanResults == None or avgSilVal == -2.0:
                continue

            if avgSilVal > bestRepeat[2]:
                bestRepeat = (kmeanResults,kmeanLabels,avgSilVal)

        if bestRepeat[0] == None:
            print 'ERROR: RunModelKmeans.py -- did not obtain results'
            return None
        
        labels = bestRepeat[1]
        avgSilVal = bestRepeat[2]
        runTime = self.get_run_time()

        ## save cluster labels (components)
        componentsFilePath = os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_classify_components.npy")
        np.save(componentsFilePath,labels)

        ## save a log file
        if verbose == True:
            print '\t...writing log file', os.path.split(__file__)[-1]

        writer = csv.writer(open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+".log"),'w'))
        
        ## for all models
        writer.writerow(["timestamp", time.asctime()])
        writer.writerow(["subsample", str(subsample)])
        writer.writerow(["project id", self.projName])
        writer.writerow(["file name", fileName])
        writer.writerow(["full model name", self.model.modelsInfo[selectedModel][0]])
        writer.writerow(["model runtime",str(round(runTime,4))])
        writer.writerow(["used channels",self.list2Str(self.includedChannelLabels)])
        writer.writerow(["unused channels",self.list2Str(self.excludedChannelLabels)])        
        writer.writerow(["number events",str(events.shape[0])])
        writer.writerow(["model mode", modelMode])

        ## model specific
        writer.writerow(["number components",str(k)])

if __name__ == '__main__':
    print 'running RunModelKmeans.py...'
    runModel = RunModelKmeans(homeDir)
    runModel.run()
