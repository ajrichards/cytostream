#!/usr/bin/env python

import numpy as np


class SilValueGenerator():
    
    def __init__(self,mat,labels):
        '''
        mat - is an n x d matrix of observations and features
        labels = is a vector of lenth n with a single assignment for each observation

        '''
        
        ## error checking
        matRows,matCols = np.shape(mat)
        if matRows != len(labels):
            print "INPUT ERROR: SilValueGenerator must have matching matrix and labels"

        self.mat = mat
        self.labels = np.array([l for l in labels])
        self.silValues = self._get_silhouette_values()
        
    def _get_silhouette_values(self):

        euclideanWithin = {}
        euclideanBetween = {}
        
        for lab in  np.sort(np.unique(self.labels)):
            indicesK = np.where(self.labels==lab)[0]
            elementsK = self.mat[indicesK,:]
            euclidDistWithin = (elementsK - elementsK.mean(axis=0))**2.0
            euclidDistWithin = np.sqrt(euclidDistWithin.sum(axis=1))

            maxEuclidDistBetween = 0.0
            euclidDistBetween = elementsK
            for nLab in np.sort(np.unique(self.labels)):
                if nLab == lab:
                    continue

                nIndices = np.where(self.labels==nLab)[0]
                nElements = self.mat[nIndices,:]
                euclidDistBetween = (elements - nElements.mean(axis=0))**2.0
                euclidDistBetween = np.sqrt(euclidDistBetween.sum(axis=1))

                if euclidDistBetween.mean() > maxEuclidDistBetween:
                    maxEuclidDistBetween = euclidDistBetween.mean()

            ## add to hash tables
            euclideanWithin[str(lab)] = euclidDistWithin
            euclideanBetween[str(lab)] = maxEuclidDistBetween

        silVals = np.zeros((self.labels.size),)
        for lab in np.sort(np.unique(self.labels)):
            indices = np.where(self.labels==lab)[0]
            a = euclideanWithin[str(lab)]
            b = np.array(euclideanBetween[str(lab)]).repeat(a.size)
            denom = b.copy()
            useA = np.where(a > b)[0]

            if len(useA) > 0:
                denom[useA] = a[useA]

            for i in range(len(a)):
                idx = indices[i]
                silVals[idx] = (b[i] - a[i]) / denom[i]

        return silVals
