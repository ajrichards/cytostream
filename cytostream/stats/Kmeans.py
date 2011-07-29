#!/usr/bin/env python

import os,sys
import numpy as np
from scipy.cluster.vq import kmeans2,kmeans
from cytostream.stats import SilValueGenerator




def get_silhouette_values(matList,matLabelList,subsample=None,minNumEvents=4):
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
                    randSelected = clusterInds[np.random.randint(0,len(clusterInds),subsample)]
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
        for clusterID in fileClusters:
            clusterElementInds = np.where(fileLabels == clusterID)[0]
            if len(clusterElementInds) < minNumEvents:
                silValues[str(fileInd)][str(clusterID)] = None
            else:
                clusterSilValue = silValuesElements[str(fileInd)][clusterElementInds].mean()
                silValues[str(fileInd)][str(clusterID)] = clusterSilValue

            del clusterElementInds
        
    return silValues


def find_noise(mat,labels,silValues=None,minNumEvents=4):
    
    ## determine which clusters are too small     
    noiseClusters = []
    numFiles = len(labels)
    uniqueClusterIDs = np.unique(labels)
    for uid in uniqueClusterIDs:
        if np.where(labels==uid)[0].size < minNumEvents:
            noiseClusters.append(noiseClusters)

    ## determine noise based on silhouette values
    if silValues != None:            
        for key,item in silValues.iteritems():
            if item < 0.0:
                noiseClusters.append(int(key))


    return noiseClusters

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
            kmeanResults, kmeanLabels = kmeans2(mat,k,minit='points')
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

    if bestK['centroids'] == None:
        print "WARNING: run_kmeans_with_sv did not return a result"

    return bestK
