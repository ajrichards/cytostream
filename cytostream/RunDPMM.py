#!/usr/bin/python
'''

output:
    a fcm.statistics.dp_cluster.ModalDPMixture object for modes
    a np.array object of the cluster assignments for modes

    a fcm.statistics.dp_cluster.DPMixture object for components
    a np.array object of the cluster assignments for components

    a run specific logfile

A. Richards
'''

import sys,getopt,os,re,cPickle,time,csv
import numpy as np
import fcm
import fcm.statistics
from cytostream import Logger,Model

if len(sys.argv) < 3:
    print sys.argv[0] + " -f fileName -p projName -k numClusters -h homeDir -s subsample -c cleanBorderEvents -v"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:h:k:s:c:v')
except getopt.GetoptError:
    print sys.argv[0] + "-f fileName -p projName"
    print "Note: fileName (-f) must be the full" 
    print "      homeDir  (-h) home directory for current project"
    print "             k (-k) the desired number of components"
    print " longModelName (-l) the long descriptive model name"
    print " subsample     (-s) subsample is t or f"
    print " clean         (-c) clean border events"
    print " verbose       (-v) verbose flag"
    sys.exit()

k = 16
name = None
verbose = False
cleanBorderEvents = True
for o, a in optlist:
    if o == '-f':
        fileName = a
    if o == '-h':
        homeDir = a
    if o == '-k':
        k = a
    if o == '-s':
        subsample = a
    if o == '-v':
        verbose = True
    if o == '-c':
        a = a.lower()
        if re.search('t|true',a):
            cleanBorderEvents = True
        else:
            cleanBorderEvents = False

## initial error checking
print 'running dpmm with %s'%k
if os.path.isdir(homeDir) == False:
    print "INPUT ERROR: not a valid project", homeDir
    sys.exit()

longModelName = "Dirichlet Process Mixture Model"
projName = os.path.split(homeDir)[-1]
projectID = os.path.split(homeDir)[-1]
loadFile = None

if re.search('\D',str(k)):
    print "INPUT ERROR: k must be numeric"
else:
    k = int(k)

## initialize a logger and a model to get specified files and channels
log = Logger()
log.initialize(projectID,homeDir,load=True)

## check to see if this is a filtering step
filterInFocus = log.log['filter_in_focus']
if filterInFocus == 'None':
    filterInFocus = None

## determine the model mode
modelMode = log.log['model_mode']
modelReference = log.log['model_reference']
modelReferenceRunID =  log.log['model_reference_run_id']

## prepare model
model = Model()
model.initialize(projectID,homeDir)
modelNum = "run%s"%int(log.log['models_run_count'])
numItersMCMC =  int(log.log['num_iters_mcmc'])

## get events
if re.search('filter',str(subsample)):
    pass
elif subsample != 'original':
    subsample = str(int(float(subsample)))

if filterInFocus == None:
    events = model.get_events(fileName,subsample=subsample)
else:
    events = model.get_events(fileName,subsample=filterInFocus)

## account for excluded channels
fileChannels = model.get_file_channel_list(fileName)
excludedChannels = log.log['excluded_channels_analysis']

if len(excludedChannels) != 0:
    includedChannels = list(set(range(len(fileChannels))).difference(set(excludedChannels)))
    includedChannelLabels = np.array(fileChannels)[includedChannels].tolist()
    excludedChannelLabels = np.array(fileChannels)[excludedChannels].tolist()
else:
    includedChannels = range(len(fileChannels))
    includedChannelLabels = fileChannels
    excludedChannelLabels = []

if len(includedChannels) + len(excludedChannels) != len(fileChannels):
    print "ERROR: Failed error sum check for excluding channels - RunDPMM.py", len(includedChannels) + len(excludedChannels), len(fileChannels)
elif type(includedChannels) != type([]) or type(excludedChannels) != type([]):
    print "ERROR: Failed error type check for excluding channels - RunDPMM.py", type(includedChannels),type(excludedChannels)

events = events[:,includedChannels]

## remove the border data points for the model fitting                                               
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

if cleanBorderEvents == True:
    nonZeroEvents = events[nonZeroInds,:]
else:
    nonZeroEvents = events

######################
# handle model running
######################

loadModel = False
if modelMode == 'onefit' and modelReference == fileName:
    loadModel = False
elif modelMode == 'onefit':
    loadModel = True

modelRunStart = time.time()
## run the model 
if loadModel == False:
    mod = fcm.statistics.DPMixtureModel(nonZeroEvents,k,last=1)
    mod.fit(verbose=True)
    full = mod.get_results()

## use a saved model
else:
    full, uselessClasses = model.load_model_results_pickle(modelReference,modelReferenceRunID,modelType='components')

modelRunStop = time.time()

## classify the components and dump
classifyComponents = full.classify(events)
if verbose == True:
    print 'RunDPMM.py - dumping components fit'

tmp1 = open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_components.pickle"),'w')
tmp2 = open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_classify_components.pickle"),'w')

cPickle.dump(full,tmp1)
cPickle.dump(classifyComponents,tmp2)
tmp1.close()
tmp2.close()

## classify the modes
modes = full.make_modal()
classifyModes = modes.classify(events)
if verbose == True:
    print 'RunDPMM.py - dumping modes fit'
print '...........................................................................................'

tmp3 = open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_modes.pickle"),'w')
tmp4 = open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_classify_modes.pickle"),'w')

cPickle.dump(modes,tmp3)
cPickle.dump(classifyModes,tmp4)
tmp3.close()
tmp4.close()



## write a log file
if verbose == True:
    print 'RunDPMM.py - writing log file'

writer = csv.writer(open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+".log"),'w'))
runTime = modelRunStop - modelRunStart

def list2Str(lst):
    strList =  "".join([str(i)+";" for i in lst])[:-1]
    if strList == '':
        return '[]'
    else:
        return strList

writer.writerow(["timestamp", time.asctime()])
writer.writerow(["subsample", str(subsample)])
writer.writerow(["project id", projName])
writer.writerow(["file name", fileName])
writer.writerow(["full model name", longModelName])
writer.writerow(["model runtime",str(round(runTime,4))])
writer.writerow(["number components",str(k)])
writer.writerow(["used channels",list2Str(includedChannelLabels)])
writer.writerow(["unused channels",list2Str(excludedChannelLabels)])
writer.writerow(["number mcmc iters",str(numItersMCMC)])
writer.writerow(["number events",str(n)])
writer.writerow(["number zero events",str(len(allZeroInds))])
writer.writerow(["zeros events removed", str(cleanBorderEvents)])
writer.writerow(["number modes",str(len(list(set(classifyModes))))])
writer.writerow(["filter used", filterInFocus])
writer.writerow(["model mode", modelMode])
if modelReference == None:
    writer.writerow(["model reference", 'None'])
else:
    writer.writerow(["model reference", modelReference])
