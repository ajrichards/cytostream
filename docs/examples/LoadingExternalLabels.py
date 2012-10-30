#!/usr/bin/env python

import os,sys,time
from sklearn.cluster import KMeans
from sklearn.preprocessing import scale
from cytostream import NoGuiAnalysis

## basic variables
projectID = 'tutorial'
currentWorkingDir = os.getcwd()
homeDir =  os.path.join(currentWorkingDir,projectID)

## specify the file path list
fileNameList = ["G69019FF_Costim_CD4.fcs", "G69019FF_SEB_CD4.fcs","G69019FF_CMVpp65_CD4.fcs"]
filePathList = [os.path.join(currentWorkingDir, fn) for fn in fileNameList]

## create a project with the files specified in filePathList
if os.path.isdir(homeDir) == False:
    nga = NoGuiAnalysis(homeDir,filePathList,autoComp=False)
else:
    nga = NoGuiAnalysis(homeDir,loadExisting=True)

## declare variables
fileNames = nga.get_file_names()
fileChannels = nga.get_file_channels()
includedChannels = ["CD4","CD8","TNF"]
includedChannelInds = [nga.channelDict[chan] for chan in includedChannels]
excludedChannels = nga.get_excluded_channels(includedChannels)
excludedChannelInds = [nga.channelDict[chan] for chan in excludedChannels]

## init the kmeans model from scikits learn
k = 3
estimator = KMeans(init='random', n_clusters=k, n_init=10)

## run the kmeans model and save results
for fileIndex, fileName in enumerate(fileNames):
    fileEvents = nga.get_events(fileName)
    data = scale(fileEvents)
    data = data[:,includedChannelInds]
    estimator.fit(data)

    ## save cluster labels
    nga.save_labels(fileName,estimator.labels_,'kmeans')

    ## save a log file for the labels
    logDict = {"timestamp":          time.asctime(),
               "project id":         projectID,
               "used channels":      includedChannels,
               "unused channels":    excludedChannels}
    nga.save_labels_log(fileName,logDict,'kmeans')

print 'kmeans done.'

## load the kmeans labels
kmeansLabels = nga.load_labels(fileName,'kmeans',getLog=False)
kmeansLabels,kmeanLog = nga.load_labels(fileName,'kmeans',getLog=True)

print 'labels', kmeansLabels
print 'log', kmeanLog
