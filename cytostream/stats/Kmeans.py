#!/usr/bin/env python

import os,sys
import numpy as np
from scipy.cluster.vq import kmeans2,kmeans,whiten
import scipy.stats as stats
from scipy.spatial.distance import pdist, squareform
from DistanceCalculator import DistanceCalculator
from SilValueGenerator import SilValueGenerator

def get_silhouette_values(matList,matLabelList,subsample=None,minNumEvents=4,resultsType='clusterMeans'):
    '''
    returns a dict of results where files are indexed by a string of the int index

    resultsType -- defines the value of

    example $> silResults = get_silhouette_values([matData1, matData2], [matLabels1, matLabs2])
    silResults 

    '''


    silValues = {}
    silValuesElements = {}
    numFiles = len(matLabelList)
    for expName in range(numFiles):
        silValues[str(expName)] = {}

    ## create subset if data for large data sets 
    subsetExpData = []
    subsetExpLabels = []

    if subsample != None:
        for expInd in range(numFiles):
            expData = matList[expInd]
            expLabels = matLabelList[expInd]
            newIndices = []

            totalInds = 0
            for cluster in np.sort(np.unique(expLabels)):
                clusterInds = np.where(expLabels==cluster)[0]
                totalInds += len(clusterInds)

                if len(clusterInds) > subsample:
                    percentTotal = float(len(clusterInds)) / float(len(expLabels)) 
                    randSelected = np.unique(clusterInds[np.random.randint(0,len(clusterInds),subsample)])
                    newIndices += randSelected.tolist()
                else:
                    newIndices += clusterInds.tolist()

            ## save indices and data
            subsetExpData.append(expData[newIndices,:])
            subsetExpLabels.append(expLabels[newIndices])

    ## calculate the silvalues for each file and the subsampled clusters
    for fileInd in range(numFiles):
            
        if subsample != None:
            fileData = subsetExpData[fileInd]
            fileLabels = subsetExpLabels[fileInd]
        else:
            fileData = matList[fileInd]
            fileLabels = matLabelList[fileInd]

        fileClusters = np.sort(np.unique(fileLabels))    
    
        ## calculate sil values
        svg = SilValueGenerator(fileData,fileLabels)
        silValuesElements[str(fileInd)] = svg.silValues
        
        ## save only sil values for each cluster
        if resultsType == 'clusterMeans':
            for clusterID in fileClusters:
                clusterElementInds = np.where(fileLabels == clusterID)[0]
                if len(clusterElementInds) < minNumEvents:
                    silValues[str(fileInd)][str(clusterID)] = None
                else:
                    clusterSilValue = silValuesElements[str(fileInd)][clusterElementInds].mean()
                    silValues[str(fileInd)][str(clusterID)] = clusterSilValue

                del clusterElementInds
        elif resultsType == 'raw':
            silValues[str(fileInd)] = svg.silValues

    return silValues

def find_noise(mat,labels,silValues=None,minNumEvents=4):
    '''
    given a np.array of data (mat) and labels return clusters that are not well fit

    exclude all silhouette values with avg values less than zero
    however if a cluster has more than 0.05% of events we include it by default

    '''

    ## determine which clusters are too small     
    noiseClusters = []
    numFiles = len(labels)
    uniqueClusterIDs = np.unique(labels)

    for uid in uniqueClusterIDs:
        if np.where(labels==uid)[0].size < minNumEvents:
            noiseClusters.append(uid)

    ## determine noise based on silhouette values
    if silValues != None:            
        for key,item in silValues.iteritems():
            if item < -0.1 or item == None :
                clusterPercent = float(np.where(labels==int(key))[0].size) / float(labels.size)
                
                if clusterPercent > 0.005:
                    continue

                noiseClusters.append(int(key))

    return list(set(noiseClusters))

def run_kmeans_with_sv(mat,kRange=[2,3,4,5,6,7,8],subsample=None):
    '''
    use kmeans and sil value to find optimal labels (and k) for a given data set
    mat - is a n x d np.array
    kRange - is the desired k to be searched

    '''

    if subsample != None:
        newIndices = []
        n,d = mat.shape

        if n > subsample:
            newIndices = np.random.randint(0,n,subsample).tolist()
        else:
            newIndices = range(n)

        toClusterMat = mat[newIndices,:]
    else:
        toClusterMat = mat

    repeats = 5
    bestK = {'centroids':None,'labels':None,'k':None,'avgSilVal':-2.0}
    for k in kRange:
        bestRepeat = (None,None,-2.0)

        #bestRepeatClusters = None
        #maxRepeatSilValue = np.array([0])
        for repeat in range(repeats):
            #try:
            kmeanResults, kmeanLabels = kmeans2(toClusterMat,k,minit='points')
            svg = SilValueGenerator(toClusterMat,kmeanLabels)
            avgSilVal = svg.silValues.mean()
            #except:
            #    kmeanResults, kmeanLabels, silVals = None, None, None
            #    print "kmeans error - ", sys.exc_info()[0]

            if kmeanResults == None or avgSilVal == -2.0:
                continue

            if avgSilVal > bestRepeat[2]:
                bestRepeat = (kmeanResults,kmeanLabels,avgSilVal)

        if bestRepeat[0] == None:
            continue

        if bestRepeat[2] > bestK['avgSilVal']:
            bestK = {'centroids':bestRepeat[0],'labels':bestRepeat[1],'k':k,'avgSilVal':bestRepeat[2]}

    ## if using subsample get centroids and reclassify the events
    if subsample != None:

        allDistances = None
        uniqueLabels = np.sort(np.unique(bestK['labels']))
        for centroid in uniqueLabels:
             centroidIndices = np.where(bestK['labels'] == centroid)[0]
             centroidMean = toClusterMat[centroidIndices,:].mean(axis=0)
             dc = DistanceCalculator()
             dc.calculate(mat,matrixMeans=centroidMean)
             distances = dc.get_distances()
             #distances = whiten(distances)
             distances = np.array([distances]).T
             if allDistances == None:
                 allDistances =  distances
             else:
                 allDistances = np.hstack([allDistances,distances])

        newLabels = np.zeros(mat.shape[0])
        
        for i in range(allDistances.shape[0]):
            newLabels[i] = uniqueLabels[np.argmin(allDistances[i,:])]

        ## adjust the centroids and labels
        bestK['labels'] = np.array([int(i) for i in newLabels])

    if bestK['centroids'] == None:
        print "WARNING: run_kmeans_with_sv did not return a result"

    return bestK
