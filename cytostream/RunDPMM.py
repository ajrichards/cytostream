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

import matplotlib as mpl
if mpl.get_backend() != 'agg':
    mpl.use('agg')

import fcm
import fcm.statistics
from cytostream import Logger,Model

if len(sys.argv) < 3:
    print sys.argv[0] + " -f fileName -p projName -g gpuDevice -h homeDir -s subsample -v"
    sys.exit()

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'f:h:s:c:v')
except getopt.GetoptError:
    print sys.argv[0] + "-f fileName -p projName"
    print "Note: fileName (-f) must be the full" 
    print "      homeDir  (-h) home directory for current project"
    print " longModelName (-l) the long descriptive model name"
    print " subsample     (-s) subsample is t or f"
    print " gpuDevice     (-g) device id for gpu"
    print " verbose       (-v) verbose flag"
    sys.exit()

k = 16
name = None
verbose = False
gpuDevice = 0
for o, a in optlist:
    if o == '-f':
        fileName = a
    if o == '-h':
        homeDir = a
    if o == '-s':
        subsample = a
    if o == '-v':
        verbose = True
    if o == '-g':
        gpuDevice = int(a)

## initial error checking
if os.path.isdir(homeDir) == False:
    print "INPUT ERROR: not a valid project", homeDir
    sys.exit()

longModelName = "Dirichlet Process Mixture Model"
projName = os.path.split(homeDir)[-1]
projectID = os.path.split(homeDir)[-1]
loadFile = None

## initialize a logger and a model to get specified files and channels
log = Logger()
log.initialize(homeDir,load=True)
selectedTransform = log.log['selected_transform']

## determine the model mode
modelMode = log.log['model_mode']
modelReference = log.log['model_reference']
modelReferenceRunID =  log.log['model_reference_run_id']
dpmmGamma = float(log.log['dpmm_gamma'])
k = int(log.log['dpmm_k'])

## prepare model
model = Model()
model.initialize(homeDir)
modelNum = "run%s"%int(log.log['models_run_count'])
numItersMCMC =  int(log.log['num_iters_mcmc'])
cleanBorderEvents = log.log['clean_border_events']

## get events
try:
    subsample = str(int(float(subsample)))
except:
    pass

## handle getting events
events = model.get_events_from_file(fileName)

if subsample != 'original':
    subsampleIndices = model.get_subsample_indices(subsample)
    events = events[subsampleIndices,:]

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
#m0 = fcm.statistics.DPMixtureModel(nclusts=nclusts, iter=niter, bunin=0, last=1)
#m0.device = n % 4 + 1
#r = m0.fit(y0)

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

modelRunStart = time.time()
## run the model 
if loadModel == False:
    if loadParams == False:
        mod = fcm.statistics.DPMixtureModel(nclusts=k,iter=numItersMCMC,burnin=0,last=1)
        mod.gamma = dpmmGamma

        ## handle gpu
        mod.device = gpuDevice
        mod.fit(nonZeroEvents,verbose=True)
        full = mod.get_results()
        tmp0 = open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_dpmm.pickle"),'w')
        cPickle.dump(full,tmp0)
        tmp0.close()
    else:
        tmp0 = open(os.path.join(homeDir,'models',modelReference+"_%s"%(modelNum)+"_dpmm.pickle"),'r')
        refMod = cPickle.load(tmp0)
        tmp0.close()
        mod = fcm.statistics.DPMixtureModel(nclusts=k,iter=numItersMCMC,burnin=0,last=1)
        mod.gamma = dpmmGamma
        mod.load_mu(refMod.mus())
        mod.load_sigma(refMod.sigmas())
        mod.load_pi(refMod.pis())
        mod.fit(nonZeroEvents,verbose=True)
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
componentsFilePath = os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_classify_components.array")
classifyComponents.tofile(componentsFilePath)

cPickle.dump(full,tmp1)
tmp1.close()

## classify the modes
modes = full.make_modal()
classifyModes = modes.classify(events)
if verbose == True:
    print 'RunDPMM.py - dumping modes fit'
print '...........................................................................................'

tmp2 = open(os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_modes.pickle"),'w')
modesFilePath = os.path.join(homeDir,'models',fileName+"_%s"%(modelNum)+"_classify_modes.array")
classifyModes.tofile(modesFilePath)

cPickle.dump(modes,tmp2)
tmp2.close()

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
writer.writerow(["model mode", modelMode])
writer.writerow(["transform", selectedTransform])

if modelReference == None:
    writer.writerow(["model reference", 'None'])
else:
    writer.writerow(["model reference", modelReference])
