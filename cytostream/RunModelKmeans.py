#!/usr/bin/python
'''
run the kmeans model on a given file
'''

__author__ = 'A. Richards'

import sys,getopt,os,re,cPickle,time,csv
import numpy as np
from cytostream import RunModelBase
from scipy.cluster.vq import kmeans2,kmeans
from cytostream.stats import get_silhouette_values

if len(sys.argv) < 3:
    print sys.argv[0] + " -f fileName -h homeDir -v -g gpuDevice"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:h:g:c:v')
except getopt.GetoptError:
    print sys.argv[0] + "-f fileName -h homeDir -g gpuDevice[optional]"
    print " Note: fileName (-f) must be the full" 
    print " homeDir        (-h) home directory for current project"
    print " gpuDevice      (-k) device id for gpu"
    print " verbose        (-v) verbose flag"
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
        """
        run specified model
        """

        if verbose == True:
            print '\t...writing log file',os.path.split(__file__)[-1]

        ## persistant parameters
        selectedModel = self.log.log['model_to_run']
        subsample = self.subsample
        modelFilter = self.log.log['model_filter']
        modelRunID = self.modelRunID
        modelReferenceRunID =  self.log.log['model_reference_run_id']
        includedChannels = self.includedChannels
        
        ## dep
        modelMode = self.log.log['model_mode']
        modelReference = self.log.log['model_reference']

        ## model specific parameters
        cleanBorderEvents = False
        k = int(self.log.log['kmeans_k'])
        repeats = int(self.log.log['kmeans_repeats'])

        ## prepare events
        events = self.model.get_events_from_file(fileName)

        if modelFilter != None:
            filterLabels = self.model.load_saved_labels(fileName,modelFilter)
            filterIndices = np.where(filterLabels==1)[0]
            events = events[filterIndices,:]
        elif subsample != 'original':
            subsampleIndices = self.model.get_subsample_indices(subsample)
            events = events[subsampleIndices,:]

        events = events[:,includedChannels]
        if cleanBorderEvents == True:
            nonBorderEvents = self.remove_border_events(events)

        ## run model
        self.start_timer()
        
        bestRepeat = (None,None,-2.0)
        for repeat in range(repeats):
            kmeanResults, kmeanLabels = kmeans2(events,k,minit='points')
            silValues = get_silhouette_values([events],[kmeanLabels],subsample=10000,
                                                  minNumEvents=3,resultsType='raw')
            avgSilVal = silValues['0'].mean()

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

        ## save cluster labels
        self.model.save_labels(fileName,labels,modelRunID)

        ## save labels log file
        logDict = self.get_labels_log()
        logDict["subsample"]        = str(subsample)
        logDict["file name"]        = fileName
        logDict["full model name"]  = re.sub('"',"",self.model.modelsInfo[selectedModel][0]),
        logDict["total runtime"]    = time.strftime('%H:%M:%S', time.gmtime(runTime))
        logDict["number events"]    = str(events.shape[0])
        logDict["model mode"]       = modelMode
        
        ## add model specific values for the logfile
        logDict["number components"] = str(k)
        logDict["repeats"]        = str(repeats)

        ## save the logfile
        if verbose == True:
            print '\t...writing log file', os.path.split(__file__)[-1]

        self.model.save_labels_log(fileName,logDict,modelRunID)

if __name__ == '__main__':
    runModel = RunModelKmeans(homeDir)
    runModel.run()
