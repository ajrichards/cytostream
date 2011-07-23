#!/usr/bin/env python

import os,sys
import numpy as np
from scipy.cluster.vq import kmeans2,kmeans
from cytostream.stats import SilValueGenerator

def run_kmeans_with_sv(mat,kRange=[2,3,4,5,6,7,8]):
    '''
    use kmeans and sil value to find optimal labels (and k) for a given data set
    mat - is a n x d np.array
    kRange - is the desired k to be searched

    '''


    repeats = 8
    bestK = {'centroids':None,'labels':None,'k':None,'avgSilVal':-2.0}
    for k in kRange:
        bestRepeat = (None,None,-2.0)

        #bestRepeatClusters = None
        #maxRepeatSilValue = np.array([0])
        for repeat in range(repeats):
            #try:
            kmeanResults, kmeanLabels = kmeans2(mat,k,minit='points')
            svg = SilValueGenerator(mat,kmeanLabels)
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
