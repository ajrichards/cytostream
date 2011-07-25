#!/usr/bin/env python

import os,sys
import numpy as np
from scipy.cluster.vq import kmeans2,kmeans
from cytostream.stats import SilValueGenerator




def get_silhouette_values(labels,expListNames,get_data_fn,subsample=None,minNumEvents=0):
    silValues = {}
    silValuesElements = {}
    for expName in expListNames:
        silValues[expName] = {}

    ## create subset if data for large data sets 
    subsetExpData = []
    subsetExpLabels = []

    if subsample != None:
        for expInd in range(len(expListNames)):
            expName = expListNames[expInd]
            expData =  get_data_fn(expName)
            expLabels = labels[expInd]
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
    for c in range(len(expListNames)):
        expName = expListNames[c]
            
        if subsample != None:
            fileData = subsetExpData[c]
            fileLabels = subsetExpLabels[c]
        else:
            fileData = get_data_fn(expName)
            fileLabels = expLabels[c]

        fileClusters = np.sort(np.unique(fileLabels))    
    
        ## calculate sil values
        svg = SilValueGenerator(fileData,fileLabels)
        silValuesElements[expName] = svg.silValues
        #silValuesElements[expName] = ._get_silhouette_values(fileData,fileLabels)
        
        ## save only sil values for each cluster
        for clusterID in fileClusters:
            clusterElementInds = np.where(fileLabels == clusterID)[0]
            if len(clusterElementInds) < minNumEvents:
                silValues[expName][str(clusterID)] = None
            else:
                clusterSilValue = silValuesElements[expName][clusterElementInds].mean()
                silValues[expName][str(clusterID)] = clusterSilValue

            del clusterElementInds
        
    return silValues

def run_kmeans_with_sv(mat,kRange=[2,3,4,5,6,7,8],subsample=None):
    '''
    use kmeans and sil value to find optimal labels (and k) for a given data set
    mat - is a n x d np.array
    kRange - is the desired k to be searched

    '''

    if subsample != None:
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
            #avgSilVal = svg.silValues.mean()
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
